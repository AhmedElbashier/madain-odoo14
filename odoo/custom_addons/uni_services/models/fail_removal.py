from cryptography.fernet import Fernet
from . import otp as otp
from odoo import api, fields, models,_
from datetime import datetime, date
from odoo.exceptions import ValidationError

class FailRemoval(models.Model):
	_name = 'fail.removal'
	_inherit = ['mail.thread']
	_rec_name = 'code'

	def get_default_employee_user(self):
		employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
		return employee_id

	student_id = fields.Many2one('uni.student',string="Name/Universit Id/Student NO", required=True)
	
	code = fields.Char(string="Code")
	
	program_id = fields.Many2one('uni.faculty.program',related='student_id.program_id', required=True, readonly=False)
	
	academic_year_id = fields.Many2one('uni.year', required=True)
	
	level_id = fields.Many2one('uni.faculty.level', required=True)
	
	semester_id = fields.Many2one('uni.faculty.semester', required=True)
	
	subject_ids = fields.One2many('fail.removal.exam','removal_id')
	
	batch_id = fields.Many2one(		
		comodel_name='uni.faculty.department.batch',
		string='Batch',
		required=True
		)
	
	registration_status = fields.Selection(string='Registration Status',
		selection=[
			('registered','Registered'),
			('not_registered','Not Registerd')
		], required=True,
		
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

	state = fields.Selection([
		("draft", "Draft"),
		("exam_committee_supervisor", "Examination Committee Supervisor"),
		('dean_approval', 'Dean Approval'),
		("wait_payment", "Wait Payment"),
		("paid", "Paid"),
		('exam_committee', 'Examination Committee'),
		('in_progress', 'In Progress'),
		('ready' , 'Ready'),
		("done", "Done"),
	], default='draft')
	
	request_date = fields.Date('Request Date', required=True, default=fields.Date.today())
	
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

	execution_start_date = fields.Date()

	execution_end_date = fields.Date()
	
	service_amount = fields.Float(string='Service Amount', required=True)

	total_amount = fields.Float(compute="_calc_total_amount", store=True)
	
	service_type_id = fields.Many2one('uni.service.type')

	resend_code = fields.Boolean(related='service_type_id.resend_code')

	is_paid = fields.Boolean(related='service_type_id.is_paid')
	
	service_name = fields.Char(required=True)
	
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

	@api.onchange('student_id')
	def onchange_student(self):
		if self.student_id:
			self.level_id = self.student_id.level_id.id 
			self.semester_id = self.student_id.semester_id.id
			self.academic_year_id = self.student_id.year_id.id
			self.batch_id = self.student_id.batch_id.id
			self.registration_status = self.student_id.registration_status
			self.academic_status = self.student_id.academic_status
			service_type_ids = self.env['uni.service.type'].search([('service_type','=','fail_removal'),('state','=','approved')])
			if service_type_ids:
				service_id = service_type_ids.search([('service_type','=','fail_removal'),('state','=','approved'),('service_amount_currency','=',self.student_id.nationality_type_id.currency_id.id)],limit=1)
				if service_id:
					self.service_type_id = service_id.id
					self.service_amount = service_id.service_amount
				else:
					self.service_type_id = service_type_ids.id
					self.service_amount = service_type_ids.service_amount


	@api.depends('subject_ids','service_amount')
	def _calc_total_amount(self):
		for rec in self:
			subtjects = rec.env['fail.removal.exam'].search_count([('removal_id','=',rec.id)])
			rec.total_amount = rec.service_amount * subtjects

	@api.model
	def create(self, vals):
		vals['code'] = self.env['ir.sequence'].next_by_code(
			'fail') or '/'
		res = super(FailRemoval, self).create(vals)
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
				'context':{'fail_removal_service_id':self.id}
			}
	def action_confirm(self):
		service_type_id = self.service_type_id
		name = 'Fail Removal'

		if not service_type_id:
			raise ValidationError(_("Service Not Found !!,Please Configure The Fail Removal Service."))

		if not self.subject_ids:
			raise ValidationError(_("You must add at least one subject."))

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
				'fail_removal_service_id':self.id,
				'invoice_line_ids':[([0,0,{'name':name,'price_unit':self.total_amount,'account_id':service_type_id.service_account.id,}])]

				})
			invoice_id.action_post()
			self.write({'state':'wait_payment','invoice_id':invoice_id.id})
		else:
			self.state = 'exam_committee'


	def to_paid(self):
		self.write({'state': 'paid'})

	def to_exam_committee(self):
		self.write({'state': 'exam_committee'})

	def action_approve(self):
		for sub in self.subject_ids:
			if not sub.exam_date:
				raise ValidationError(_('Please determine the examination dates'))

		if self.service_type_id.require_pickup_delivery:
			self.write({'execution_start_date':date.today(),'state': 'in_progress'})
		else:
			self.state = 'done'

	def action_ready(self):
		key = Fernet.generate_key()
		self.key = key.decode("utf-8") 
		password = otp.generateOTP()
		print('----------------- self.password',password,self.key)
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
              'context': {'fail_removal_service_id':self.id}
              
        }
		self.state = 'done'

	def to_draft(self):
		self.write({'state': 'draft'})



class FailExam(models.Model):
	_name = 'fail.removal.exam'

	subject_id = fields.Many2one('uni.faculty.subject', domain=[('fail_remove','=',True)])	
	academic_year_id = fields.Many2one('uni.year', string='Fail Year')
	level_id = fields.Many2one('uni.faculty.level', string='Fail Level')
	semester_id = fields.Many2one('uni.faculty.semester', string='Fail Term')
	exam_academic_year_id = fields.Many2one('uni.year', string='Exam Year')
	exam_level_id = fields.Many2one('uni.faculty.level', string='Exam Level')
	exam_semester_id = fields.Many2one('uni.faculty.semester', string='Exam Term')
	exam_date = fields.Date()
	removal_id = fields.Many2one('fail.removal')
