# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _
from datetime import datetime,date
from odoo.exceptions import ValidationError

class RegistrationRecord(models.Model):
	_name = 'uni.registration.record'
	_description = 'Registration Record'
	_inherit = ['mail.thread']
	_rec_name = "code"

	name = fields.Char('Name', required=True)

	code = fields.Char("Code", required=True, readonly=True, default=lambda self: _('New'))

	start_date = fields.Date('Start Date')

	end_date = fields.Date('End Date')

	academic_year_id = fields.Many2one(
		'uni.year',
		string="Academic Year",
		required=True
	)

	level_id = fields.Many2one(
		'uni.faculty.level',
		string="Level",
		required=True
	)

	program_registration_ids = fields.One2many(
		comodel_name='uni.program.registration',
		inverse_name='registration_id'
	)

	student_ids = fields.One2many('uni.student','register_id',compute="_get_students")

	registration_fees_ids = fields.One2many('uni.registered.fees',inverse_name='registration_record_id')

	state = fields.Selection([
		('draft', "Draft"),
		('approved', "Approved"),
		('closed', "Closed"),
	],
		default='draft'
	)

	def _get_students(self):
		for rec in self:
			batchs = [reg_id.batch_id.id for reg_id in rec.program_registration_ids]
			rec.student_ids = self.env['uni.student'].search([('batch_id','in',batchs),('state','=','student')])

	def action_approve(self):
		program_registration_id = self.program_registration_ids.search([('registration_id','=',self.id),('state','!=','approved')])
		if program_registration_id:
			raise ValidationError(
				_("There is a program registration record not approved yet!!")
				)
		else:
			#if self.level_id.order != '1':
			for program in self.program_registration_ids:
				program.create_registration_request()
			self.state = 'approved'


	def action_close(self):
		self.state = 'closed'

	def rest_draft(self):
		self.state = 'draft'

	def write(self, values):
		res = super(RegistrationRecord, self).write(values)
		for program in self.program_registration_ids:
			program.onchange_dates()
		return res
		   
	@api.model
	def create(self, values):
		if values.get('code', _('New')) == _('New'):
			academic_year_id = self.env['uni.year'].browse(values['academic_year_id'])
			code_sequence = self.env['ir.sequence'].next_by_code('registration.record.sequence') or _('New')
			values['code'] = academic_year_id.code+ '-' + str(code_sequence)

		res = super(RegistrationRecord, self).create(values)
		return res




class ProgramRegistration(models.Model):
	_name = 'uni.program.registration'
	_inherit = ['mail.thread']
	_description = 'Program Registration'


	program_id = fields.Many2one('uni.faculty.program', string="Program", required=True)

	batch_id = fields.Many2one(
		'uni.faculty.department.batch',
		domain="[('program_id','=',program_id)]",
		string="Batch",
		required=True)

	batch_students = fields.Integer('Batch students',compute="_get_students_number")
	
	registered_students = fields.Integer('Registered students',compute="_get_students_number")
	
	unregistered_students = fields.Integer('Unregistered students',compute="_get_students_number")

	start_date = fields.Date('Start Date')

	end_date = fields.Date('End Date') 

	registration_id = fields.Many2one('uni.registration.record')

	installment_ids = fields.One2many(
		comodel_name='uni.fees.installment',
		inverse_name="program_registration_id",
		)

	state = fields.Selection([
		('draft', "Draft"),
		('approved', "Approved"),
		('closed', "Closed"),
	],
		default='draft'
	)

	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)


	def _get_students_number(self):
		for rec in self:
			rec.batch_students = self.env['uni.student'].search_count([('batch_id','=',rec.batch_id.id),('state','=','student'),('academic_status','not in',['supplement','substitutions','substitutional_supplement','dismiss'])])
			rec.registered_students = self.env['uni.student'].search_count([('batch_id','=',rec.batch_id.id),('state','=','student'),('registration_status','=','registered'),('academic_status','not in',['supplement','substitutions','substitutional_supplement','dismiss'])])
			rec.unregistered_students = self.env['uni.student'].search_count([('batch_id','=',rec.batch_id.id),('state','=','student'),('registration_status','not in',['registered','rejected']),('academic_status','not in',['supplement','substitutions','substitutional_supplement','dismiss'])])

	def onchange_dates(self):
		if self.installment_ids:
			dates = [installment.start_date for installment in self.batch_id.batch_installment_ids]
			if dates:
				start_date = min(dates)
				batch_installment_id = self.env['uni.fees.installment'].search([('program_registration_id','=',self.id),('start_date','=',start_date)],limit=1)
				if batch_installment_id:
					if self.start_date and not self.end_date:
						batch_installment_id.write({'start_date':self.start_date})
					elif self.end_date and not self.start_date:
						batch_installment_id.write({'end_date':self.end_date})
					elif self.end_date and self.start_date:
						batch_installment_id.write({'start_date':self.start_date,'end_date':self.end_date})


	def check_student_discounts(self,student):
		request_ids = self.env['uni.discount_scholarship.request'].search([('student_id','=',student.id),('state','=','approved')])
		amount = 0.0
		percentage = 0.0
		discount_amount = 0.0
		name = ''
		if request_ids:
			for request in request_ids:
				if request.type_of_dis == 'discount':
					if request.siblings:
						if amount < request.first_brother_percentage:
							amount = request.first_brother_percentage
							percentage = request.first_brother_percentage
							request_ids = request
					else:
						if amount < request.percentage:
							amount = request.percentage
							percentage = request.percentage
							request_ids = request
				else:
					if amount < request.percentage:
						amount = request.percentage
						request_ids = request

			if request_ids.type_of_dis == 'discount':
				name = 'Discount Amount'
				discount_amount =  (student.tuition_fees*percentage/100)
			else:
				name = 'Scholarship Amount'
				discount_amount = (student.tuition_fees*request_ids.percentage/100)

		return percentage,discount_amount,request_ids


	def calculate_student_fees(self,student):
		tuition_fees = 0.0
		registration_fees = 0.0
		record_fees_id = self.env['uni.registered.fees'].search([('nationality_type_id','=',student.nationality_type_id.id),('registration_record_id','=',self.registration_id.id)],limit=1)
		if record_fees_id:
			registration_fees = record_fees_id.registration_fees
		else:
			fees_increse_percenatge = student.admission_year.fees_increse_percenatge
			if fees_increse_percenatge <= 0 :
				raise ValidationError(
				_("The increse percentage must be greater than zero")
				)
			registration_fees = student.registration_fees+student.registration_fees*fees_increse_percenatge/100
		
		tuition_fees = student.tuition_fees

		return tuition_fees,registration_fees

	def create_repeat_discount_record(self,student):
		discount_record_id = self.env['uni.discount.scholarship'].search([('repeat','=',True)],limit=1)
		if not discount_record_id:
			raise ValidationError(
				_("Please configure the repeat discount")
				)
		discount_record = self.env['uni.discount_scholarship.request'].create({
			'type_of_dis':'discount',
			'type':'student',
			'student_id':student.id,
			'academic_year_id':student.year_id.id,
			'admission_year_id':student.admission_year.id,
			'discount_scholarship_id':discount_record_id.id,
			'percentage':student.year_id.discount_percentage,
			'fees_amount':student.tuition_fees,
			'start_date':date.today(),
			'state':'approved',
			})

		return discount_record.percentage,discount_record.discounted_amount,discount_record



	def create_registration_request(self):
		student_ids = self.env['uni.student'].search([('state','=','student'),('batch_id','=',self.batch_id.id)])
		discount_record = self.env['uni.discount_scholarship.request']
		discount_amount = 0.0
		percentage = 0.0

		for student in student_ids:
			student.write({'registration_status':'not_registered'})
			installment = []
			if student.academic_status in ['repeat','repeat_subjects'] and self.registration_id.academic_year_id.allow_discount:
				percentage,discount_amount,discount_record = self.create_repeat_discount_record(student)

			else:
				percentage,discount_amount,discount_record = self.check_student_discounts(student)
			
			tuition_fees,registration_fees = self.calculate_student_fees(student)
			if self.registration_id.academic_year_id.allow_installment:
				for fees in self.installment_ids:
					amount = 0.0
					if self.registration_id.academic_year_id.discount_payment == 'equally':
						amount = discount_amount/len(self.installment_ids)
					else:
						if fees.first_installment == False:
							amount = discount_amount
					installment.append([0,0,{'name':fees.name,
						'installment_percentage':tuition_fees*fees.installment_percentage/100,
						'discount_amount':amount,
						'start_date':fees.start_date,
						'end_date':fees.end_date,
						'first_installment':fees.first_installment,
						'include_registration_fees':fees.include_registration_fees,
						}])
			else:
				installment.append([0,0,{'name':'1',
					'installment_percentage':tuition_fees,
					'discount_amount':discount_amount,
					'start_date':self.registration_id.start_date,
					'end_date':self.registration_id.end_date,
					'first_installment':True,
					'include_registration_fees':True,
					}])

			self.env['uni.registration.request'].create({
				'student_id':student.id,
				'academic_year_id':self.registration_id.academic_year_id.id,
				'admission_year_id':student.admission_year.id,
				'program_id':student.program_id.id,
				'level_id':student.level_id.id,
				'semester_id':student.semester_id.id,
				'state':'draft',
				'tuition_fees':tuition_fees,
				'registration_fees':registration_fees,
				'fees_installment_ids':installment,
				'batch_id':student.batch_id.id,
				'discount_perc':percentage,
				'discounted_amount':discount_amount,
				'total_amount':(tuition_fees-discount_amount),
				'discount_record':discount_record.id,
				'state':'approved',
				})
			student.write({'registration_fees':registration_fees})


	def action_program_approve(self):
		self.state = 'approved'

	def action_close(self):
		self.state = 'closed'

	def rest_draft(self):
		self.state = 'draft'

class RegistrationRequest(models.Model):
	_name = 'uni.registration.request'
	_description = 'Registration Request'
	_inherit = ['mail.thread']
	_rec_name = 'student_id'

	student_id = fields.Many2one(
		'uni.student',
		string="Student"
		)

	academic_year_id = fields.Many2one(
		'uni.year',
		string='Academic Year'
		)

	admission_year_id = fields.Many2one(
		'uni.year',
		string='Admission Year'
		)

	program_id = fields.Many2one('uni.faculty.program', related='student_id.program_id')

	batch_id = fields.Many2one('uni.faculty.department.batch')

	level_id = fields.Many2one('uni.faculty.level')


	semester_id = fields.Many2one('uni.faculty.semester', string="Term")

	currency_id = fields.Many2one('res.currency', related='student_id.nationality_type_id.currency_id')

	invoice_id = fields.Many2one('account.move')
	
	tuition_fees = fields.Float('Tuition Fees')

	registration_fees = fields.Float('Registration Fees')

	fees_installment_ids = fields.One2many('uni.fees.installment', inverse_name="registration_request_id")

	discount_perc = fields.Float('Discount Perc(%)')

	discounted_amount = fields.Float('Discount Amount')

	total_amount = fields.Float()

	discount_record = fields.Many2one('uni.discount_scholarship.request')

	state = field_name = fields.Selection([
		('draft', 'Draft'),
		('approved', 'Approved'),
		('closed','Closed'),
	],default='draft')

	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)
	registration_steps_ids = fields.One2many('registration.steps.directions', related='company_id.registration_steps_ids')
	guidelines_financial_management  = fields.One2many('guidelines.financial.management', related='company_id.guidelines_financial_management')
	is_paid = fields.Boolean(compute="_check_paid")

	@api.depends('invoice_id')
	def _check_paid(self):
		for rec in self:
			rec.is_paid = False
			if rec.invoice_id.state == 'posted':
				rec.is_paid = True
				

	@api.onchange('is_paid')
	def _is_paid(self):
		for rec in self:
			if rec.invoice_id.state == 'posted':
				rec.student_id.registration_status = 'registered'

	
	@api.onchange('student_id')
	def onchange_student(self):

		self.academic_year_id = self.student_id.year_id.id 
		self.level_id = self.student_id.level_id.id 
		self.semester_id = self.student_id.semester_id.id 
		self.batch_id = self.student_id.batch_id.id

	def action_approve(self):
		self.state = 'approved'

	def action_close(self):
		self.state = 'closed'

	def rest_draft(self):
		self.state = 'draft'
