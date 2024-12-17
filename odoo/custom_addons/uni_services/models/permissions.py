from cryptography.fernet import Fernet
from . import otp as otp
from datetime import datetime, date
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class StudentPermissions(models.Model):
	_name = 'uni.student.permissions'
	_inherit = ['mail.thread']
	_description = 'Student Permissions'
	_rec_name = 'code'

	def get_default_employee_user(self):
		employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
		return employee_id

	name = fields.Many2one('uni.student', string="Name/Universit Id/Student NO", required=True)

	permission_type = fields.Selection([
		('medical_ornaic', 'medical_ornaic'),
		('travel_permission', 'travel_permission'),
		('entry_permission', 'entry_permission'),
	],)

	entry_permission_type = fields.Selection([
		('entry', 'Faculty Entry'),
		('lecture', 'Lecture Entry'),
		('exam', 'Exam Entry'),
		('eminentes', 'Eminent-es'),
	],string="Permission Type")

	permission_period = fields.Date(default=date.today(),string="Period From")
	permission_period_to = fields.Date(default=date.today(),string="To")

	code = fields.Char(string='Code', readonly=True)

	program_id = fields.Many2one(
		string="Program",
		comodel_name="uni.faculty.program",
		required=True,
	)

	level_id = fields.Many2one(
		string="Level",
		comodel_name="uni.faculty.level",
		required=True,
	)

	semester_id = fields.Many2one(
		string="Term",
		comodel_name="uni.faculty.semester",
		required=True,
	)

	academic_status = fields.Selection(
		string="Acadimic Status",
		selection=[
            ('fresh', 'Fresh'),
            ('success', 'Success'),
            ('repeat', 'Repeat'),
            ('repeat_subjects','Repeat for Subjects'),
            ('appendix' , 'Has Appendixs'),
            ('substitutions', 'Has Substitutions'),
            ('substitutional_supplement','Substitutional&Appendix'),
            ('dismiss','Dismiss'),
        ],
		default='fresh',required=True,
	)
	batch_id = fields.Many2one(
		comodel_name='uni.faculty.department.batch',
		string='Batch',
		required=True
		)


	year_id = fields.Many2one('uni.year', required=True,string="Academic Year")

	registration_status = fields.Selection(string='Registration Status',
		selection=[
			('registered','Registered'),
			('not_registered','Not Registerd')
		], required=True,
		)


	procedure_type = fields.Selection([
		('substitutional_request', 'Substitutional Request'),
		('lecture_attending', 'Lecture Attending'),
		('both', 'Both'),
	])

	request_date = fields.Date('Request Date', default=fields.Date.today())
	
	permission_reason = fields.Char(string='Reason')

	coordinator_recommendation = fields.Text('Coordinator')

	scientific_affairs_recommendation = fields.Text('Scientific Affairs')

	dean_decision = fields.Text('Dean Decision')

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

	service_executor = fields.Many2one('hr.employee',default=get_default_employee_user)

	service_type_id = fields.Many2one('uni.service.type')

	resend_code = fields.Boolean(related='service_type_id.resend_code')

	is_paid = fields.Boolean(related='service_type_id.is_paid')

	execution_start_date = fields.Date()

	execution_end_date = fields.Date()

	start_date = fields.Date()

	end_date = fields.Date()

	service_name = fields.Char(required=True)

	service_amount = fields.Float()

	priority = fields.Selection([
		('0', 'Low'),
		('1', 'High'),
	], default='0', string="Priority")

	state = fields.Selection([
		('draft', 'Draft'),
		('requested', 'Requested'),
		('under_payment','Under Payment'),
		('coordinator','Coordinator'),
		('scientific_affairs','Scientific Affairs'),
		('dean_decision','Dean decision'),
		('in_progress', 'In Progress'),
		('ready' , 'Ready'),
		('done', 'Done'),
		('rejected', 'Rejected'),
	],default="draft")

	password = fields.Char()

	key = fields.Char()

	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)

	@api.onchange('name')
	def onchange_student(self):
		if self.name:
			self.program_id = self.name.program_id.id,
			self.level_id = self.name.level_id.id
			self.semester_id = self.name.semester_id.id
			self.academic_status = self.name.academic_status
			self.batch_id = self.name.batch_id.id
			self.year_id = self.name.year_id.id
			self.registration_status = self.name.registration_status
			permission_type = ''
			if self.permission_type == 'travel_permission':
				service_type_ids = self.env['uni.service.type'].search([('service_type','=','travel_permission'),('state','=','approved')])
				permission_type = 'travel_permission'
			elif self.permission_type == 'medical_ornaic':
				service_type_ids = self.env['uni.service.type'].search([('service_type','=','medical_ornaic'),('state','=','approved')])
				permission_type = 'medical_ornaic'
			elif self.permission_type == 'entry_permission':
				service_type_ids = self.env['uni.service.type'].search([('service_type','=','entry_permission'),('state','=','approved')])
				permission_type = 'entry_permission'

			if service_type_ids:
				service_id = service_type_ids.search([('service_type','=',permission_type),('state','=','approved'),('service_amount_currency','=',self.name.nationality_type_id.currency_id.id)],limit=1)
				if service_id:
					self.service_type_id = service_id.id
					self.service_amount = service_id.service_amount
				else:
					self.service_type_id = service_type_ids.id
					self.service_amount = service_type_ids.service_amount


	def action_reject(self):
		self.state = 'rejected'

	def rest_draft(self):
		self.state = 'draft'

	def action_request(self):
		if self.name.university_id:
			self.action_confirm()
		else:
			return {
				'name': _('Confirmation Wizard'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'confirm.wizard',
				'type': 'ir.actions.act_window',
				'target':'new',
				'context':{'permission_service_id':self.id}
			}

	def action_confirm(self):
		service_type_id = self.env['uni.service.type']
		name = ''
		if self.permission_type == 'travel_permission':
			service_type_id = service_type_id.search([('service_type','=','travel_permission')],limit=1)
			if not service_type_id:
				raise ValidationError(_("Service Not Found !!,Please Configure Travel Permission Service."))
			name = 'Travel Permission'
		elif self.permission_type == 'medical_ornaic':
			service_type_id = service_type_id.search([('service_type','=','medical_ornaic')],limit=1)
			if not service_type_id:
				raise ValidationError(_("Service Not Found !!,Please Configure Medical Ornaic Service."))
			name = 'Medical Ornaic'
		elif self.permission_type == 'entry_permission':
			service_type_id = service_type_id.search([('service_type','=','entry_permission')],limit=1)
			if not service_type_id:
				raise ValidationError(_("Service Not Found !!,Please Configure Entry Permission Service."))
			name = 'Entry Permission'

		if self.is_paid:
			if not service_type_id.service_account:
				raise ValidationError(_("Please Configure The Service Account."))

			if service_type_id.is_paid == True and service_type_id.service_amount == 0.00:
				raise ValidationError(_("The Service Amount Must Be More Than Zero."))

			if not self.company_id.service_journal_id:
				raise ValidationError(_("Please Configure The Service Journal From Setting"))

			invoice_id = self.env['account.move'].create({
				'partner_id':self.name.partner_id.id,
				'invoice_date':date.today(),
				'currency_id':service_type_id.service_amount_currency.id,
				'move_type':'out_invoice',
				'journal_id':self.company_id.service_journal_id.id,
				'permission_service_id':self.id,
				'invoice_line_ids':[([0,0,{'name':name,'account_id':service_type_id.service_account.id,'price_unit':self.service_amount}])]

				})
			invoice_id.action_post()
			self.invoice_id = invoice_id.id
			self.state = 'under_payment'

		else:
			if self.permission_type == 'medical_ornaic' or self.permission_type == 'entry_permission':
				if self.service_type_id.require_pickup_delivery:
					self.write({'execution_start_date':date.today(),'state': 'in_progress'})
				else:
					self.write({'state':'done'})
			else:
				self.state = 'coordinator'

	def action_coordinator(self):
		self.state = 'coordinator'

	def action_scientific_affairs(self):
		self.state = 'scientific_affairs'

	def action_dean_decision(self):
		self.state = 'dean_decision'

	def action_approve(self):
		if self.service_type_id.require_pickup_delivery:
			self.write({'execution_start_date':date.today(),'state': 'in_progress'})
		else:
			self.state = 'done'

	def action_ready(self):
		key = Fernet.generate_key()
		self.key = key.decode("utf-8") 
		password = otp.generateOTP()
		print('----------------- self.password',password)
		self.password = otp.encrypt(password.encode(), key).decode("utf-8") 
		if not self.execution_end_date:
			self.write({'execution_end_date':date.today(),'state': 'ready'})

	def action_done(self):
		return {
              'name': _('OTP Confirmations'),
              'type': 'ir.actions.act_window',
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'otp.wizard',
              'target': 'new',
              'context': {'permission_service_id':self.id}
              
        }
		self.state = 'done'


	@api.model
	def create(self, values):
		if values['permission_type'] == 'medical_ornaic':
			values['code'] =self.env['ir.sequence'].next_by_code('medical_ornaic') or '/'
		if values['permission_type'] == 'travel_permission':
			values['code'] =self.env['ir.sequence'].next_by_code('travel_perm') or '/'
		if values['permission_type'] == 'entry_permission':
			values['code'] =self.env['ir.sequence'].next_by_code('entry.permission') or '/'
		return super(StudentPermissions, self).create(values)
