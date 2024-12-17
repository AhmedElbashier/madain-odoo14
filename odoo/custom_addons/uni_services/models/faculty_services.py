from cryptography.fernet import Fernet
from . import otp as otp
from odoo import api, fields, models,_
from datetime import datetime, date
from odoo.exceptions import ValidationError

class Services(models.Model):
	_name = 'uni.service.type'
	_inherit = ['mail.thread']
	_rec_name = 'name'

	code = fields.Char(string="Code", readonly=True)
	
	name = fields.Char(string="Name", required=True)
	
	type = fields.Selection([
		('registration','Registration'),
		('admission','Admission')
	])
	
	registration_service_type = fields.Selection([
		('registration','Registration'),
		('registration_admission','Registration and Admission'),
		],default='registration', required=True, string="Service For")
	
	admission_service_type = fields.Selection([
		('admission','Admission'),
		('admission_registration','Admission and Registration'),
		],default='admission', required=True, string="Service For")
	
	is_paid = fields.Boolean(string="Is paid ?" )
	
	service_amount = fields.Float(string='Service Amount')
	
	service_amount_currency = fields.Many2one('res.currency',string='Currency')
	
	service_account = fields.Many2one('account.account',string='Account')
	
	journal_id = fields.Many2one('account.journal')
	
	service_notification = fields.Boolean(string="Send Notification" )
	
	sms_notification = fields.Boolean(string="SMS")
	
	whatsapp_notification = fields.Boolean(string="Whatsapp")
	
	email_notification = fields.Boolean(string="Email")	
	
	notification_type = fields.Selection(selection=[
		('sms','SMS'),('whatsapp','Whatsapp'),('email','Email'),
	])
	whatsapp_notification=fields.Boolean(string="whatsapp")
	
	sms_notification=fields.Boolean(string='SMS')
	
	email_notification=fields.Boolean(string='Email')
	
	service_type = fields.Selection([
		('late_registration','Late Registraion'),
		('travel_permission','Travel Permission'),
		('medical_ornaic','Medical Ornaic'),
		('entry_permission','Entry Permission'),
		('recorrection','Recorrection'),
		('substitutions','Substitutions'),
		('fail_removal','Fail Removal'),
		('frozen','Study Suspension'),
		('resignation','Resignation'),
		('academic_record','Academic Form'),
		('travel_settlement','Travel Settlement'),
		('card_lost','Card Loss'),
		('enrollment_certificate','Enrollment Certificate'),
	], string="Type")

	paper_type = fields.Selection([
		("normal", "عادي"),
		("stamped", "مختوم"),
		("locked", "مؤمن")])
	
	require_pickup_delivery = fields.Boolean(string="Requires pick-up and delivery Docs?")

	resend_code = fields.Boolean()

	state = fields.Selection([
		('draft', "Draft"),
		('approved', "Approved"),
		('closed', "Closed"),
	],
		default='draft'
	)

	def action_approve(self):
		self.state = 'approved'

	def action_close(self):
		self.state = 'closed'

	def rest_draft(self):
		self.state = 'draft'

	@api.constrains('name','code')
	def _check_name(self):
		for record in self:
			service_id = self.search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)],limit=1)
			if service_id:
				raise ValidationError(_("There is another service with the same name or code: %s" % service_id.name))
	
	@api.model
	def create(self, vals):
		if vals['type'] == 'registration':
			vals['code'] = self.env['ir.sequence'].next_by_code(
			'service.type.registration') or '/'
		else:
			vals['code'] = self.env['ir.sequence'].next_by_code(
			'service.type.admission') or '/'
		res = super(Services, self).create(vals)
		return res


	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError(_('The type must be in dratf state to be deleted.'))
			else:
				return super(Services, self).unlink()



class GeneralServices(models.Model):
	_name = 'uni.general.services'
	_inherit = ['mail.thread']
	_rec_name = 'ref'

	def get_default_employee_user(self):
		employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
		return employee_id

	student_id = fields.Many2one('uni.student',string="Name/Universit Id/Student NO" ,required=True)
	
	program_id = fields.Many2one('uni.faculty.program',related='student_id.program_id', required=True)
	
	academic_year_id = fields.Many2one('uni.year', required=True)
	
	level_id = fields.Many2one('uni.faculty.level', required=True)
	
	semester_id = fields.Many2one('uni.faculty.semester', required=True)
	
	batch_id = fields.Many2one(
		comodel_name='uni.faculty.department.batch',
		string='Batch',
		required=True
		)
	
	type_admission = fields.Selection(
		selection=[
			('new_admission', 'New Admission'),
			('mature' , 'Mature'),
			('bridging' , 'Bridging'),
			('transfer' , 'Transfer')
		],default='new_admission',string='Admission Type', related='student_id.type_admission', required=True
	)
	
	registration_status = fields.Selection(string='Registration Status',
		selection=[
			('registered','Registered'),
			('not_registered','Not Registerd')
		], required=True,)
	
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
	
	admission_year = fields.Many2one('uni.year', required=True)
	
	ref = fields.Char(string="Code")
	
	paper_type = fields.Selection([
		("normal", "عادي"),
		("stamped", "مختوم"),
		("locked", "مؤمن")], default='normal')
	
	certificate_perpose = fields.Text()
	
	sattlement_reason = fields.Text('Reason for settlement')
	
	reason = fields.Selection(selection=[
		('loss','Loss'),
		('harm','Harm')])
	
	request_date = fields.Date('Request Date', required=True, default=fields.Date.today())
	
	operation_type = fields.Selection(selection=[
		('academic_record','Academic Record Form'),
		('enrollment_certificate','University enrollment certificate'),
		('travel_settlement','Travel Settlement'),
		('lost_card','Card Loss'),
	], string="Service Name", required=True)
	
	state = fields.Selection([
		("draft", "Draft"),
		("under_request", "Under Request"),
		("wait_payment", "Wait Payment"),
		("paid", "Paid"),
		("in_progress", "In Progress"),
		("delivery", "Delivery"),
		("done", "Done")], default='draft')
	
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
	
	language = fields.Many2many('res.lang')
	
	printing_date = fields.Date('Printing Date')
	
	delivery_date = fields.Date('Delivery Date')

	service_type_id = fields.Many2one('uni.service.type')

	resend_code = fields.Boolean(related='service_type_id.resend_code')

	is_paid = fields.Boolean(related='service_type_id.is_paid')
	
	service_executor = fields.Many2one('hr.employee',default=get_default_employee_user)

	execution_start_date = fields.Date()

	execution_end_date = fields.Date()
	
	service_amount = fields.Float(string='Service Amount')

	total_amount = fields.Float(compute="_calc_total_amount", store=True)
	
	start_date = fields.Date('Execution Start Date')
	
	end_date = fields.Date('Execution End Date')
	
	password = fields.Char()
	
	key = fields.Char()
	
	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)

	@api.onchange('operation_type','paper_type')
	def onchange_operation_type(self):
		service_type_ids = self.env['uni.service.type']
		self.service_type_id = False
		if self.operation_type:
			service_type = ''
			if self.operation_type == 'academic_record':
				service_type_ids = self.env['uni.service.type'].search([('service_type','=','academic_record'),('paper_type','=',self.paper_type),('state','=','approved')])
				service_type = 'academic_record'
			elif self.operation_type == 'enrollment_certificate':
				service_type_ids = self.env['uni.service.type'].search([('service_type','=','enrollment_certificate'),('state','=','approved')])
				service_type = 'enrollment_certificate'
			elif self.operation_type == 'travel_settlement':
				service_type_ids = self.env['uni.service.type'].search([('service_type','=','travel_settlement'),('state','=','approved')])
				service_type = 'travel_settlement'
			elif self.operation_type == 'lost_card':
				service_type_ids = self.env['uni.service.type'].search([('service_type','=','card_lost'),('state','=','approved')])
				service_type = 'card_lost'


			if service_type_ids:
				service_id = service_type_ids.search([('service_type','=',service_type),('paper_type','=',self.paper_type),('state','=','approved'),('service_amount_currency','=',self.student_id.nationality_type_id.currency_id.id)],limit=1)
				if service_id:
					self.service_type_id = service_id.id
					self.service_amount = service_id.service_amount
				else:
					self.service_type_id = service_type_ids.id
					self.service_amount = service_type_ids.service_amount
			domain = {}
			domain = {
				'domain':{
					'service_type_id':[('service_type','=',service_type),('paper_type','=',self.paper_type),('state','=','approved')],
					
				}
			}
	   
			return domain

	@api.onchange('student_id')
	def onchange_student(self):
		if self.student_id:
			self.level_id = self.student_id.level_id.id 
			self.batch_id = self.student_id.batch_id.id 
			self.semester_id = self.student_id.semester_id.id
			self.academic_year_id = self.student_id.year_id.id
			self.admission_year = self.student_id.admission_year
			self.academic_status = self.student_id.academic_status
			self.registration_status = self.student_id.registration_status
			
	@api.depends('language','service_type_id','paper_type','operation_type')
	def _calc_total_amount(self):
		for rec in self:
			if rec.language and rec.operation_type in ['academic_record','enrollment_certificate']:
				languages = len(self.language.ids)
				rec.total_amount = languages*rec.service_amount
			else:
				rec.total_amount = rec.service_amount


	@api.model
	def create(self, vals):
		vals['ref'] = self.env['ir.sequence'].next_by_code(
			'service.request.seq') or '/'
		res = super(GeneralServices, self).create(vals)
		return res

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
				'context':{'general_service_id':self.id}
			}

	def action_confirm(self):
		service_type_id = self.env['uni.service.type']
		name = ''
		if self.operation_type == 'academic_record':
			service_type_id = service_type_id.search([('service_type','=','academic_record')],limit=1)
			if not service_type_id:
				raise ValidationError(_("Service Not Found !!,Please Configure The Academic Record Form Service."))
			name = 'Academic Record Form'
		elif self.operation_type == 'enrollment_certificate':
			service_type_id = service_type_id.search([('service_type','=','enrollment_certificate')],limit=1)
			if not service_type_id:
				raise ValidationError(_("Service Not Found !!,Please Configure Enrollment Certificate Service."))
			name = 'University enrollment certificate'
		elif self.operation_type == 'travel_settlement':
			service_type_id = service_type_id.search([('service_type','=','travel_settlement')],limit=1)
			if not service_type_id:
				raise ValidationError(_("Service Not Found !!,Please Configure Travel Settlement Service."))
			name = 'Travel Settlement'
		elif self.operation_type == 'lost_card':
			service_type_id = service_type_id.search([('service_type','=','card_lost')],limit=1)
			if not service_type_id:
				raise ValidationError(_("Service Not Found !!,Please Configure Card Loss Service."))
			name = 'Lost Card'

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
				'service_id':self.id,
				'invoice_line_ids':[([0,0,{'name':name,'price_unit':self.total_amount,'account_id':service_type_id.service_account.id,}])]
				})
			invoice_id.action_post()
			self.invoice_id = invoice_id.id
			self.state = 'wait_payment'
		else:
			if self.service_type_id.require_pickup_delivery:
				self.write({'start_date':date.today(),'state': 'in_progress'})
			else:
				self.write({'state':'done'})

	def to_request(self):
		self.write({'state': 'under_request'})

	def to_paid(self):
		self.write({'state': 'paid'})

	def in_progress(self):
		self.write({'start_date':date.today(),'state': 'in_progress'})

	def to_delivery(self):
		key = Fernet.generate_key()
		self.key = key.decode("utf-8") 
		password = otp.generateOTP()
		print('----------------- self.password',password)
		self.password = otp.encrypt(password.encode(), key).decode("utf-8") 
		if not self.execution_end_date:
			self.write({'end_date':date.today(),'state': 'delivery'})

	def to_complete(self):
		return {
              'name': _('OTP Confirmations'),
              'type': 'ir.actions.act_window',
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'otp.wizard',
              'target': 'new',
              'context': {'general_service_id':self.id}
              
        }
		self.write({'state': 'complete'})

	def to_draft(self):
		self.write({'state': 'draft'})
		