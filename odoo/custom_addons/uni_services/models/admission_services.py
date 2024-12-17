from cryptography.fernet import Fernet
from . import otp as otp
from odoo import api, fields, models,_
from datetime import datetime, date
from odoo.exceptions import ValidationError

class AdmissionServices(models.Model):
	_name = 'admission.services'
	_inherit = ['mail.thread']
	_rec_name = 'ref'

	def get_default_employee_user(self):
		employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
		return employee_id
		
	student_id = fields.Many2one('uni.admission',required=True)
	
	ref = fields.Char(string="Code")
	
	program_id = fields.Many2one('uni.faculty.program',related='student_id.program_id', required=True, readonly=False)
	
	academic_year_id = fields.Many2one('uni.year', required=True)
	
	batch_id = fields.Many2one(
		comodel_name='uni.faculty.department.batch',
		string='Batch',
		required=True
		)
	
	request_date = fields.Date('Request Date', required=True, default=fields.Date.today())
	
	service_executor = fields.Many2one('hr.employee',default=get_default_employee_user)
	
	execution_start_date = fields.Date()

	execution_end_date = fields.Date()

	service_type_id = fields.Many2one('uni.service.type',domain=[('admission_service_type','in',['admission','admission_registration'])])
	
	resend_code = fields.Boolean(related='service_type_id.resend_code')

	service_name = fields.Char()
	
	service_amount = fields.Float(string='Service Amount')
	
	service_amount_currency = fields.Many2one('res.currency',string='Currency')
	
	state = fields.Selection([
		('draft', "Draft"),
		('wait_payment', "Wait Payment"),
		('in_progress',"In Progress"),
		('ready',"Ready For Delivery"),
		('done',"Done"),
	],default='draft')
	
	is_paid = fields.Boolean(string="Is paid ?",related='service_type_id.is_paid' )
	
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
	
	password = fields.Char()
	
	key = fields.Char()
	
	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)

	@api.onchange('student_id')
	def onchange_student(self):
		if self.student_id:
			self.program_id = self.student_id.program_id.id,
			self.batch_id = self.student_id.batch_id.id
			self.academic_year_id = self.student_id.acadimic_year_id.id

	@api.onchange('service_type_id')
	def _get_amount(self):
		self.service_amount = self.service_type_id.service_amount
		self.service_amount_currency = self.service_type_id.service_amount_currency


	@api.model
	def create(self, vals):
		vals['ref'] = self.env['ir.sequence'].next_by_code(
			'admission.services') or '/'
		res = super(AdmissionServices, self).create(vals)
		return res

	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError(_('The service must be in dratf state to be deleted.'))
			else:
				return super(AdmissionServices, self).unlink()


	# def action_request(self):
	# 	if self.student_id.university_id:
	# 		self.action_draft()
	# 	else:
	# 		return {
	# 			'name': _('Confirmation Wizard'),
	# 			'view_type': 'form',
	# 			'view_mode': 'form',
	# 			'res_model': 'confirm.wizard',
	# 			'type': 'ir.actions.act_window',
	# 			'target':'new',
	# 		}
	
	def action_draft(self):
		if not self.company_id.service_journal_id:
			raise ValidationError(_("Please Configure The Service Journal From Setting"))

		if self.service_type_id.is_paid:
			invoice_id = self.env['account.move'].create({
				'partner_id':self.student_id.user_id.partner_id.id,
				'invoice_date':date.today(),
				'currency_id':self.service_amount_currency.id,
				'move_type':'out_invoice',
				'journal_id':self.company_id.service_journal_id.id,
				'admission_service_id':self.id,
				'invoice_line_ids':[([0,0,{'name':self.service_type_id.name,'price_unit':self.service_amount,'account_id':self.service_type_id.service_account.id,}])]
			})
			invoice_id.action_post()
			self.write({'state':'wait_payment','invoice_id':invoice_id.id})

		else:
			self.state = 'in_progress'


	def action_in_progress(self):
		self.state = 'in_progress'

	def action_ready(self):
		if self.service_type_id.require_pickup_delivery:
			key = Fernet.generate_key()
			self.key = key.decode("utf-8") 
			password = otp.generateOTP()
			print('----------------- self.password',password)
			self.password = otp.encrypt(password.encode(), key).decode("utf-8") 
			if not self.execution_end_date:
				self.write({'execution_end_date':date.today(),'state': 'ready'})
		else:
			self.state = 'done'

	def action_complete(self):
		return {
              'name': _('OTP Confirmations'),
              'type': 'ir.actions.act_window',
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'otp.wizard',
              'target': 'new',
              'context': {'admission_service_id':self.id}
              
        }
		self.state = 'done'


