# -*- encoding: utf-8 -*-
from datetime import datetime, date
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class Year(models.Model):
	_name = 'uni.year'
	_description = 'Academic Year'
	_inherit = ['mail.thread']
	_rec_name = "name"

	name = fields.Char('Name', required=True)

	code = fields.Char("Code")

	program_ids = fields.Many2many(
		string="Admission Programs",
		comodel_name="uni.faculty.program",
		domain=[('state','=','approved')],
	)

	calendar_ids = fields.One2many(
		comodel_name="uni.faculty.calendar",
		inverse_name="academic_year_id",
		string="Calendars"
	)

	registration_record_ids = fields.One2many(
		'uni.registration.record',
		'academic_year_id',
		)

	admission_record_ids = fields.One2many(
		'uni.admission.record',
		'academic_year_id',
		)

	study_fees_id = fields.Many2one('uni.study_fees', compute='compute_fees', inverse='fees_inverse', store=True)

	fees_id = fields.One2many(
		comodel_name="uni.study_fees",
		inverse_name='year_id',
		string="Fees"
	)

	start_date = fields.Date('Start Date', required=True)

	end_date = fields.Date('End Date', required=True)

	allow_discount = fields.Boolean('Allow Discount')

	discount_percentage = fields.Float('Discount Perc(%)')

	allow_installment = fields.Boolean('Allow Installment')

	can_be_repeated = fields.Boolean('Re-repeate')

	active = fields.Boolean(string="Active", default=True)

	state = fields.Selection([
		('draft','Draft'),
		('approved','Approved'),
		('closed','Closed')
		],
		default='draft',
		)

	fees_installment_ids = fields.One2many(
		comodel_name='uni.fees.installment',
		inverse_name="uni_year_id",
		copy=True,
		)

	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)

	fees_increse_percenatge = fields.Integer(string='Fees Increse Perc(%)', default=lambda self: self.env.user.company_id.fees_increse_percenatge)

	first_year = fields.Boolean(compute="get_first_year")

	last_code = fields.Char(default=lambda self: self.env.user.company_id.last_year_code)

	draft_records = fields.Boolean(compute='compute_draft_records')

	@api.constrains('name','code','study_fees_id','first_year')
	def _check_name(self):
		for record in self:	
			year_id = self.search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)],limit=1)
			if year_id:
				raise ValidationError(_("There is another year with the same name or code: %s" % year_id.name))

			year_fees_id = self.search([('study_fees_id','=',record.study_fees_id.id),('study_fees_id','!=',False),('id','!=',record.id)],limit=1)
			if year_fees_id:
				raise ValidationError(_("There is another year with a same fees record: %s" % year_fees_id.name))

			if not self.last_code and not self.code:
				raise ValidationError(_("The code field is required when creating the first year in the system"))

	@api.depends('fees_id')
	def compute_fees(self):
		if len(self.fees_id) > 0:
			self.study_fees_id = self.fees_id[0]

	def fees_inverse(self):
		if len(self.fees_id) > 0:
			# delete previous reference
			fees = self.env['uni.study_fees'].browse(self.fees_id[0].id)
			fees.year_id = False
		# set new reference
		self.study_fees_id.year_id = self

	def compute_draft_records(self):
		self.draft_records = False
		for rec in self:
			admission_record_id = rec.admission_record_ids.search([('state','=','approved'),('academic_year_id','=',self.id)])
			registration_record_id = rec.registration_record_ids.search([('state','=','approved'),('academic_year_id','=',self.id)])
			if admission_record_id:
				rec.draft_records = True
		# for rec in self.admission_record_ids:
		# 	if rec.state == 'approved':
		# 		self.write({'draft_records':True})
		# 		break
		# 	else:
		# 		continue
		# if not self.draft_records:
		# 	for rec in self.registration_record_ids:
		# 		if rec.state == 'approved':
		# 			self.write({'draft_records':True})
		# 			break
		# 		else:
		# 			continue

	def get_first_year(self):
		for rec in self:
			year_ids = self.search([('id','!=',rec._origin.id)])
			if year_ids:
				rec.first_year = True
			else:
				rec.first_year = False
				
	def to_approved(self):
		self.check_discount_scholarship()
		self.create_records()
		self.check_student_status()
		self.write({'state': 'approved'})

	def to_closed(self):
		self.write({'state': 'closed'})

	def reset_to_draft(self):
		for rec in self.registration_record_ids:
			for program in rec.program_registration_ids:
				program.unlink()
			rec.unlink()

		for rec in self.admission_record_ids:
			for batch in rec.batch_ids:
				batch.unlink()
			rec.unlink()


		self.write({'state': 'draft'})

	def check_student_status(self):
		student_ids = self.env['uni.student'].search([('academic_status','in',['repeat','repeat_subjects'])])
		for student in student_ids:
			if student.level_id.order != '1':
				level = int(student.level_id.order)-1
			else:
				level = 1
			level_id = self.env['uni.faculty.level'].search([('order','=',str(level))],limit=1)
			batch_id = self.env['uni.faculty.department.batch'].search([('level_id','=',level_id.id),('program_id','=',student.program_id.id)],limit=1)
			if not batch_id:
				installments = []
				for fees in student.batch_id.batch_installment_ids:
					installments.append([0,0,{'name':fees.name,
						'installment_percentage':fees.installment_percentage,
						'start_date':fees.start_date,
						'end_date':fees.end_date,
						'include_registration_fees':fees.include_registration_fees,
						'first_installment':fees.first_installment,
					}])
				batch_id = self.env['uni.faculty.department.batch'].create({
						'name':student.program_id.name+'.',
						'program_id':student.program_id.id,
						'curriculum_id':student.program_id.curriculum_id.id,
						'academic_year_id':self.id,
						'admission_year_id':self.id,
						'state':'new',
						'batch_installment_ids':installments,
						})
				batch_id.write({'name':student.program_id.name+' '+batch_id.code})
				batch_id.action_study()
				registration_record_id = self.env['uni.registration.record'].search([('level_id.order','=','1'),('academic_year_id','=',self.id)],limit=1)
				self.env['uni.program.registration'].create({
					'program_id':student.program_id.id,
					'batch_id':batch_id.id,
					'registration_id':registration_record_id.id,
					'installment_ids':installments,
					})
			student.write({
				'batch_id':batch_id.id,
				})

	def check_discount_scholarship(self):
		request_ids = self.env['uni.discount_scholarship.request'].search([('discount_scholarship_id.discount_scholarship_type','=','yearly')])
		for request in request_ids:
		    request.write({
		        'state':'closed',
		        'end_date':date.today()
		        })

	def get_installment_records(self):
		'''
			Get The Installments Break Down In This Year
		'''
		values = []
		for fees in self.fees_installment_ids:
			values.append([0,0,{'name':fees.name,
								'installment_percentage':fees.installment_percentage,
								'start_date':fees.start_date,
								'end_date':fees.end_date,
								'include_registration_fees':fees.include_registration_fees,
								'first_installment':fees.first_installment,
			}])
		return values

	def get_registration_fees_records(self):
		'''
			Get The Registraion Fees In This Year
		'''
		values = []
		fees_id = self.env['uni.study_fees'].search([('year_id','=',self.id)],limit=1)
		if not fees_id:
			raise ValidationError(
				_("Please Configure The Registration and Tuition Fees")
				)
		
		for reg in fees_id.registered_line_ids:
			values.append([0,0,{'nationality_type_id':reg.nationality_type_id.id,
				'registration_fees':reg.registration_fees}])
		return values

	def create_admission_records(self):
		admission_record_id = self.env['uni.admission.record'].create({
			'name':'Admission Record'+'/'+self.code,
			'academic_year_id':self.id,
			'start_date':self.start_date,
			'end_date':self.end_date
			})

		nationality_ids = self.env['uni.nationality.type'].search([])
		for program in self.program_ids:
			if nationality_ids:
				for nationality in nationality_ids:
					admission_record_id.admission_program_plan_ids.create({
						'program_id':program.id,
						'nationality_type_id':nationality.id,
						'admission_record_id':admission_record_id.id,
					})
			else:
				admission_record_id.admission_program_plan_ids.create({
						'program_id':program.id,
						'admission_record_id':admission_record_id.id,
					})
		return admission_record_id

	def create_registration_record(self,level):

		start_date = self.start_date
		end_date = self.end_date
		if self.allow_installment:
			dates = [installment.start_date for installment in self.fees_installment_ids]
			if dates:
				start_date = min(dates)
				end_date = self.fees_installment_ids.search([('start_date','=',start_date)],limit=1).end_date


		registration_record_id = self.env['uni.registration.record'].create({
					'name':'Registration Record Level '+level.order,
					'academic_year_id':self.id,
					'level_id':level.id,
					'start_date':start_date,
					'end_date':end_date
				})

		return registration_record_id

	def create_records(self):
		fees_id = self.env['uni.study_fees'].search([('year_id','=',self.id)],limit=1)
		if not fees_id:
			raise ValidationError(
				_("Please Configure The Fees Of This Year")
				)
		
		level_ids = self.env['uni.faculty.level'].search([])
		if self.program_ids:
			admission_record_id = self.create_admission_records()
		installments = self.get_installment_records()
		for level in level_ids:
			if (level.order == '1') and self.program_ids:
				registration_record_id = self.create_registration_record(level)
				for record in self.program_ids:
					registration_fees_ids = self.get_registration_fees_records()
					batch_id = self.env['uni.faculty.department.batch'].create({
						'name':record.name,
						'program_id':record.id,
						'curriculum_id':record.curriculum_id.id,
						'academic_year_id':self.id,
						'admission_year_id':self.id,
						'state':'new',
						'batch_installment_ids':installments,
						'admission_record_id':admission_record_id.id,
						'registered_fees_ids':registration_fees_ids,
						})

					batch_id.write({'name':record.name+' '+batch_id.code})
					registration_record_id.program_registration_ids.create({
						'program_id':record.id,
						'batch_id':batch_id.id,
						'registration_id':registration_record_id.id,
						'installment_ids':installments,
						})

			else:
				batch_ids = self.env['uni.faculty.department.batch'].search([('next_level_id','=',level.id),('state','=','under_study')])
				semester_id = self.env['uni.faculty.semester'].search([('order','=','1')],limit=1)
				if batch_ids:
					registration_record_id = self.create_registration_record(level)
					for batch in batch_ids:
						registration_record_id.program_registration_ids.create({
								'program_id':batch.program_id.id,
								'batch_id':batch.id,
								'registration_id':registration_record_id.id,
								'installment_ids':installments,
								})
						batch.batch_installment_ids.unlink()
						batch.write({
							'academic_year_id':self.id,
							'batch_installment_ids':installments,
							'level_id':batch.next_level_id.id,
							'semester_id':semester_id.id,
							'next_level_id':False,
							})
						student_ids = self.env['uni.student'].search([('batch_id','=',batch.id),('academic_status','=','success')])
						for student in student_ids:
							student.write({
								'level_id':batch.level_id.id,
								'semester_id':batch.semester_id.id
								})

	@api.model
	def create(self, values):
		company_id = self.env['res.company'].browse(values['company_id'])

		if values['last_code']:
			code1 = int(values['last_code'].partition('-')[0])
			code2 = int(values['last_code'].partition('-')[2])
			values['code'] = str(code1+1)+"-"+str(code2+1)

		company_id.last_year_code = values['code']
		res = super(Year, self).create(values)
		return res


class Installment(models.Model):
	_name = 'uni.fees.installment'
	# _order = 'id asc'

	name = fields.Char('Name')

	installment_percentage = fields.Float('Installment')

	start_date = fields.Date('Start Date')

	end_date = fields.Date('End Date')

	uni_faculty_batch = fields.Many2one('uni.faculty.department.batch')

	program_registration_id = fields.Many2one('uni.program.registration')

	uni_year_id = fields.Many2one('uni.year')    

	registration_request_id = fields.Many2one('uni.registration.request')

	registration_fees = fields.Float(related='registration_request_id.registration_fees')

	include_registration_fees = fields.Boolean()

	first_installment = fields.Boolean()

	discount_amount = fields.Float()

	due_amount = fields.Float('Due Amount', compute='_compute_due_amount')

	currency_id = fields.Many2one('res.currency',related='registration_request_id.currency_id')

	invoice_id = fields.Many2one('account.move')

	invoice_state = fields.Selection([('draft','Draft'),('posted','Posted'),('cancel','Cancelled')],string="Invoice Status",related='invoice_id.state') 
	
	payment_state = fields.Selection(selection=[
		('not_paid', 'Not Paid'),
		('in_payment', 'In Payment'),
		('paid', 'Paid'),
		('partial', 'Partially Paid'),
		('reversed', 'Reversed'),
		('invoicing_legacy', 'Invoicing App Legacy')],
		string="Payment Status",related='invoice_id.payment_state')

	state = fields.Selection([('draft','Draft'),('approved','Approved')])

	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)

	def _compute_due_amount(self):
		for rec in self:
			if rec.include_registration_fees:
				rec.due_amount = rec.installment_percentage - rec.discount_amount + rec.registration_request_id.registration_fees
			else:
				rec.due_amount = rec.installment_percentage - rec.discount_amount

	@api.model
	def write(self,values):
		res = super(Installment, self).write(values)
		fees_id = False
		if self.include_registration_fees:
			if self.program_registration_id:
				fees_id = self.env['uni.fees.installment'].search([('program_registration_id','=',self.program_registration_id.id),('include_registration_fees','=',True),('id','!=',self.id)])
			elif self.registration_request_id:
				fees_id = self.env['uni.fees.installment'].search([('registration_request_id','=',self.registration_request_id.id),('include_registration_fees','=',True),('id','!=',self.id)])
			if fees_id:
				raise ValidationError(
						_("The Registration Fees Only Paid With One Installment")
					)
		return res


	def action_create_invoice(self):
		registration_fees_account_id = self.company_id.registration_fees_account_id.id
		tuition_fees_account_id = self.company_id.tuition_fees_account_id.id
		journal_id = self.company_id.journal_id.id

		if not registration_fees_account_id or not tuition_fees_account_id or not journal_id:
			raise ValidationError(_("Please Configure The Accounting Fees Information From Setting"))

		invoice_line_values = [([0,0,{'name':'Tuition Fees','account_id':tuition_fees_account_id,'price_unit':self.installment_percentage}])]
		discount_amount = 0.0
		if self.include_registration_fees:
			invoice_line_values.append([0,0,{'name':'Registration Fees','account_id':registration_fees_account_id,'price_unit':self.registration_request_id.registration_fees}])
		current_date = date.today()
		if current_date <= self.end_date :
			invoice_date = current_date
		else : invoice_date = self.end_date
		invoice_id = self.env['account.move'].create({
			'partner_id':self.registration_request_id.student_id.partner_id.id,
			'invoice_date': invoice_date,
			'invoice_date_due' : self.end_date,
			'move_type':'out_invoice',
			'journal_id':journal_id,
			'currency_id':self.registration_request_id.currency_id.id,
			'invoice_line_ids':invoice_line_values,
			'installment_id':self.id
			})
		invoice_id.action_post()
		if self.registration_request_id.discounted_amount > 0:
			if self.registration_request_id.admission_year_id.discount_payment == 'equally':

				installment_count = self.registration_request_id.fees_installment_ids.search_count([('registration_request_id','=',self.registration_request_id.id)])
				discount_amount = self.registration_request_id.discounted_amount/installment_count
				self.create_payment(discount_amount)
			else:
				installment_id = self.registration_request_id.fees_installment_ids.search([('registration_request_id','=',self.registration_request_id.id),('first_installment','=',False)],limit=1)
				if not self.first_installment:
					discount_amount = self.registration_request_id.discounted_amount
					self.create_payment(discount_amount)
		
		self.invoice_id = invoice_id.id

		
		################ update registration_status for student ########################
		if self.first_installment and self.payment_state == 'paid':
			self.registration_request_id.student_id.registration_status = 'registered'
		self.state="approved"

	def create_payment(self,discount_amount):
		payment_id = self.env['account.payment'].create({
				'partner_id':self.registration_request_id.student_id.partner_id.id,
				'date':date.today(),
				'payment_type': 'inbound',
				'amount':discount_amount,
				'currency_id':self.registration_request_id.currency_id.id,
				'ref':'Discounts&Scholarship',
				})
		payment_id.action_post()

	def create_outstanding_invoice(self):
		installment_ids = self.search([('start_date','<=',date.today())])
		if installment_ids:
			for rec in installment_ids:
				rec.action_create_invoice()