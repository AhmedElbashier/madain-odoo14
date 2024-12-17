from cryptography.fernet import Fernet
from . import otp as otp
from odoo import api, fields, models , _
from odoo.exceptions import ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class StudentServices(models.Model):
	_name = 'uni.faculty.student.services'
	_inherit = ['mail.thread']
	_rec_name = 'student_id'

	def get_default_employee_user(self):
		employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
		return employee_id
		
	service_type = fields.Selection(selection=[('resignation','Resignation'),('frozen','Suspension')])
	
	student_id = fields.Many2one('uni.student', string="Name/Universit Id/Student NO")

	university_id= fields.Char('uni.student',related='student_id.university_id')
	
	resignation_sequence = fields.Char('Code',readonly=True)
	
	frozen_sequence = fields.Char('Code',readonly=True)
	
	program_id = fields.Many2one('uni.faculty.program',related='student_id.program_id', readonly=False, required=True)
	
	academic_year_id = fields.Many2one('uni.year', required=True)
	
	level_id = fields.Many2one('uni.faculty.level', required=True)
	
	semester_id = fields.Many2one('uni.faculty.semester', required=True)
	
	academic_status = fields.Selection(
		string="Acadimic Status",
		selection=[
            ('fresh', 'Fresh'),
            ('success', 'Success'),
            ('repeat', 'Repeat'),
            ('repeat_subjects','Repeat for Subjects'),
            ('supplement' , 'Has Supplements'),
            ('substitutions', 'Has Substitutions'),
            ('substitutional_supplement','Substitutional&Appendix'),
            ('dismiss','Dismiss'),
        ], required=True)
	
	batch_id = fields.Many2one(
		comodel_name='uni.faculty.department.batch',
		string='Batch',
		required=True
		)

	registration_status = fields.Selection(string='Registration Status',
		selection=[
			('registered','Registered'),
			('not_registered','Not Registerd')
		], required=True)

	request_date = fields.Date(default=fields.Date.today())
	
	reason = fields.Text()

	state = fields.Selection(
		selection=[
			('draft', 'Draft'),
			('under_payment', 'Under Payment'),
			('program_coordinator', 'Program Coordinator'),
			('dean' , 'Dean'),
			('in_progress', 'In Progress'),
			('ready' , 'Ready'),
			('done' , 'Done'),
		],default="draft")

	resume_date = fields.Date()

	invoice_id = fields.Many2one('account.move', string="Invoice")

	invoice_state = fields.Selection([('draft','Draft'),('posted','Posted'),('cancel','Cancelled')],string="Invoice Status",related='invoice_id.state')
	
	payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Payment Status",related='invoice_id.payment_state')

	service_type_id = fields.Many2one('uni.service.type')

	resend_code = fields.Boolean(related='service_type_id.resend_code')

	is_paid = fields.Boolean(related='service_type_id.is_paid')
	
	service_executor = fields.Many2one('hr.employee',default=get_default_employee_user)
	
	service_name = fields.Char(required=True)

	service_amount = fields.Float()
	
	execution_start_date = fields.Date()
	
	execution_end_date = fields.Date()
	
	priority = fields.Selection([
		('0', 'Low'),
		('1', 'High'),
	], default='0', string="Priority")

	password = fields.Char()
	
	key = fields.Char()

	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)

	@api.constrains('student_id')
	def check_student_payments(self):
		if self.service_type == 'frozen':
			amount = 0
			registration_request_id = self.env['uni.registration.request'].search([('student_id','=',self.student_id.id),('academic_year_id','=',self.academic_year_id.id)],limit=1)
			installment_ids = self.env['uni.fees.installment'].search([('registration_request_id','=',registration_request_id.id),('state','=','approved')])
			for line in installment_ids:
				amount += line.invoice_id.amount_total-line.invoice_id.amount_residual
			total_fees = registration_request_id.registration_fees+registration_request_id.tuition_fees*50/100
			if amount < total_fees:
				raise ValidationError(_("Sorry, the student must have paid 50'%'' of the fees."))

		else:
			registration_request_id = self.env['uni.registration.request'].search([('student_id','=',self.student_id.id),('academic_year_id','=',self.academic_year_id.id)],limit=1)
			installment_ids = self.env['uni.fees.installment'].search([('registration_request_id','=',registration_request_id.id),'|',('payment_state','!=','paid'),('state','!=','approved')])
			if installment_ids:
				raise ValidationError(_("Sorry, the student must have paid his all academic year fees."))

	@api.onchange('student_id')
	def onchange_student(self):
		self.level_id = self.student_id.level_id.id 
		self.semester_id = self.student_id.semester_id.id
		self.academic_year_id = self.student_id.year_id.id
		self.registration_status = self.student_id.registration_status
		self.academic_status = self.student_id.academic_status
		self.batch_id = self.student_id.batch_id.id
		self.university_id = self.student_id.university_id
		service_type = ''
		if self.service_type == 'resignation':
			service_type_ids = self.env['uni.service.type'].search([('service_type','=','resignation'),('state','=','approved')])
			service_type = 'resignation'
		elif self.service_type == 'frozen':
			service_type_ids = self.env['uni.service.type'].search([('service_type','=','frozen'),('state','=','approved')])
			service_type = 'frozen'

		if service_type_ids:
			service_id = service_type_ids.search([('service_type','=',service_type),('state','=','approved'),('service_amount_currency','=',self.student_id.nationality_type_id.currency_id.id)],limit=1)
			if service_id:
				self.service_type_id = service_id.id
				self.service_amount = service_id.service_amount
			else:
				self.service_type_id = service_type_ids.id
				self.service_amount = service_type_ids.service_amount


	def action_request(self):
		if self.student_id.university_id:
			self.action_confirm()
		else:
			return {
				'name': _('Confirmation Wizard'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'confirm.wizard',
				'type': 'ir.actions.act_window',
				'target':'new',
				'context':{'student_services_id':self.id}
			}
	def action_confirm(self):
		service_type_id = self.service_type_id
		name = ''
		if not service_type_id:
			raise ValidationError(_("Service Not Found !!,Please Configure The Service."))

		if self.service_type == 'resignation':
			name = 'Resignation'
		else:
			name = 'Suspension'
		
		if self.is_paid:
			if not service_type_id.service_account:
				raise ValidationError(_("Please Configure The Service Account."))

			if service_type_id.is_paid == True and service_type_id.service_amount == 0.00:
				raise ValidationError(_("The Service Amount Must Be More Than Zero."))

			if not self.company_id.service_journal_id:
				raise ValidationError(_("Please Configure The Service Journal From Setting"))

			invoice_id = self.env['account.move'].create({
				'partner_id':self.student_id.partner_id.id,
				'invoice_date':date.today(),
				'currency_id':service_type_id.service_amount_currency.id,
				'move_type':'out_invoice',
				'journal_id':self.company_id.service_journal_id.id,
				'student_service_id':self.id,
				'invoice_line_ids':[([0,0,{'name':name,'price_unit':self.service_amount,'account_id':service_type_id.service_account.id,}])]
				})
			invoice_id.action_post()
			self.invoice_id = invoice_id.id
			self.state = 'under_payment'
		else:
			self.state = 'program_coordinator'

	# def to_request(self):
	# 	self.write({'state':'under_request'})

	def to_program_coordinator(self):
		self.write({'state':'program_coordinator'})

	def to_dean(self):
		self.write({'state':'dean'})

	def in_progress(self):
		if self.service_type_id.require_pickup_delivery:
			self.write({'execution_start_date':date.today(),'state': 'in_progress'})
		else:
			if self.service_type == 'resignation':
				self.student_id.write({'state':'resigned', 'resignation_date': date.today()})
				discount_ids = self.env['uni.discount_scholarship.request'].search([('student_id','=',self.student_id.id)])
				for discount in discount_ids:
					discount.write({'state':'closed','end_date':date.today()})

			if self.service_type == 'frozen':
				self.student_id.write({'state':'frozen'})

			self.state = 'done'

	def to_ready(self):
		key = Fernet.generate_key()
		self.key = key.decode("utf-8") 
		password = otp.generateOTP()
		print('----------------- self.password',password)
		self.password = otp.encrypt(password.encode(), key).decode("utf-8") 
		if not self.execution_end_date:
			self.write({'execution_end_date':date.today(),'state': 'ready'})


	def to_done(self):
		context = {}
		if self.service_type == 'resignation':
			self.student_id.write({'state':'resigned', 'resignation_date': date.today()})
			discount_ids = self.env['uni.discount_scholarship.request'].search([('student_id','=',self.student_id.id)])
			for discount in discount_ids:
				discount.write({'state':'closed','end_date':date.today()})
			context = {'resignation_id':self.id}

		if self.service_type == 'frozen':
			self.student_id.write({'state':'frozen'})
			context = {'suspension_id':self.id}

		return {
              'name': _('OTP Confirmations'),
              'type': 'ir.actions.act_window',
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'otp.wizard',
              'target': 'new',
              'context': context
              
        }
		self.write({'state':'done'})

	def to_draft(self):
		self.write({'state':'draft'})


	@api.model
	def create(self, values):
		if values['service_type'] == 'resignation':
			values['resignation_sequence'] = self.env['ir.sequence'].next_by_code(
			'student.resignation') or '/'
			res = super(StudentServices, self).create(values)

		if values['service_type'] == 'frozen':
			values['frozen_sequence'] = self.env['ir.sequence'].next_by_code(
			'student.frozen') or '/'
			res = super(StudentServices, self).create(values)

		return res

	@api.constrains('request_date')
	def check_validity(self):
		if self.service_type == 'frozen':
			std_frozen_ids = self.search([
				('student_id','=',self.student_id.id),
				('service_type','=','frozen'),
				('state','=','done')])

			if std_frozen_ids:
				prev_year =  self.request_date + relativedelta(years=-1)
				prev_year = prev_year.year

				for rec in std_frozen_ids:
					if rec.request_date.year == prev_year:
						raise ValidationError(_("Sorry, You can't request for Suspension during two consecutive years.. "))
			if len(std_frozen_ids) >= 2:
				raise ValidationError(_("Sorry, You can't request for Suspension more than 2 time.."))

	@api.onchange('request_date','resume_date')
	def check_resume_date(self):
		if self.request_date and self.resume_date:
			if self.resume_date < self.request_date:
				raise ValidationError(_("Sorry, Resume date must be grater than request date.. "))

	# def unlink(self):
	# 	for rec in self:
	# 		if rec.state != 'draft':
	# 			raise ValidationError(_('The service must be in dratf state to be deleted.'))
	# 		else:
	# 			return super(StudentServices, self).unlink()


class Student(models.Model):
	_inherit = 'uni.student'

	resignation_date = fields.Date()
