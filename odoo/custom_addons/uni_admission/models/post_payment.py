from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime, timedelta



class fees(models.Model):
	_inherit = 'student.fees'

	def create_payment(self):
		return {
			'name': _('Student Payment'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'post.student.payment',
			'type': 'ir.actions.act_window',
			'target':'new',
			'context':{
				'default_student_id':self.student_id.id,
				'default_amount': self.sub_total - self.paid_amount,
				'default_fees_line_id':self.id,
				'default_description':self.semester_id.name,
				'default_currency_id':self.student_id.currency_id.id,
				}

		}
	def create_invoice(self):
		print('---------- create_invoice')
	# 	partner_id = self.env['res.partner'].search([('name','=',self.student_id.university_id)])
	# 	invoice_line_id = self.env['account.invoice.line']
	# 	if not self.env.user.company_id.fees_income_account or not self.env.user.company_id.reg_income_account:
	# 		msg = "Please check that the income and registration account is correctly set"
	# 		raise Warning(
	# 			 _(msg)
	# 			)
	# 	invoice_id = self.env['account.invoice'].create({
	# 		'partner_id': partner_id.id,
	# 		'state': 'draft',
	# 		'account_id': self.env.user.company_id.receivable_fees_account.id,
	# 		'type': 'out_invoice',
	# 		'currency_id': self.student_id.currency_id.id,
	# 		'level_id':self.level_id.id,
	# 		'semester_id':self.semester_id.id
	# 		})
		
	# 	invoice_line_id.create({
	# 		'invoice_id': invoice_id.id,
	# 		'account_id': self.env.user.company_id.fees_income_account.id,
	# 		'name':  'Income Fees',
	# 		'price_unit': self.study_fees,
	# 	})

	# 	invoice_line_id.create({
	# 		'invoice_id': invoice_id.id,
	# 		'account_id': self.env.user.company_id.reg_income_account.id,
	# 		'name':  'Registration Fees',
	# 		'price_unit': self.registration_fees,
	# 	})

	# 	invoice_line_id.create({
	# 		'invoice_id': invoice_id.id,
	# 		'account_id': self.env.user.company_id.discount_account.id,
	# 		'name':  'Discount',
	# 		'price_unit': -(self.total_discount),
	# 	})

	# 	for fee in self.other_fees:
	# 		if not fee.account_id:
	# 			msg = "Please configure "+ fee.name +" account"
	# 			raise Warning(
	# 			 _(msg)
	# 			)
	# 		invoice_line_id.create({
	# 		'invoice_id': invoice_id.id,
	# 		'account_id': fee.account_id.id,
	# 		'price_unit': fee.amount,
	# 		'name':  fee.name,
	# 			})
	# 	self.write({
	# 		'invoice_id':invoice_id.id,
	# 		'state':'open'
	# 		})

class Admission(models.Model):
	_name = "post.student.payment"

	student_id = fields.Many2one('uni.student', 'Student Number', required=True)
	amount = fields.Float('Amount', required=True)

	journal_id = fields.Many2one(
		'account.journal', 'Journal', required=True)
	fees_line_id = fields.Many2one('student.fees')
	description = fields.Char('Description', required=True)
	currency_id = fields.Many2one(
		'res.currency', string='Currency', required=True,)
	payment_type = fields.Selection([('cash','Cash'),('bank','Bank'),('check','Check'),('transfer','Bank Transfer')],'Payment Type',default='cash',required=True)
	check_number = fields.Char('Check Number')
	account_number = fields.Char('Account Number')

	@api.onchange('currency_id')
	def _onchange_currency(self):
		self.amount = abs(self._compute_payment_amount())
		# Set by default the first liquidity journal having this currency if exists.
		journal = self.env['account.journal'].search(
		    [('type', 'in', ('bank', 'cash')), ('currency_id', '=', self.fees_line_id.student_id.currency_id.id)], limit=1)
		if journal:
			return {'value': {'journal_id': journal.id}}

	def _compute_payment_amount(self, invoices=None, currency=None):
		'''
		Compute the total amount for the payment wizard.
		'''
		# Get the payment currency
		if not currency:
			payment_currency = self.currency_id
		if payment_currency == self.fees_line_id.student_id.currency_id:
			return self.fees_line_id.sub_total - self.fees_line_id.paid_amount
		else:
			return self.fees_line_id.student_id.currency_id._convert(self.amount, payment_currency, self.env.user.company_id, fields.Date.today())

	def get_first_level(self, student_id):
		domain = [('faculty_id', '=', student_id.faculty_id.id)]
		level = self.env['uni.faculty.level'].search(
			domain, limit=1, order="order asc")
		semester = self.env['uni.faculty.semester'].search(
			domain, limit=1, order="order asc")
		return level, semester

	def Post_payment(self):

		partner_id = self.env['res.partner'].search([('ref','=',self.student_id.university_id)])
		self.create_payment(partner_id)
		paid_amount = self.fees_line_id.paid_amount + self.amount
		student_faculty = self.fees_line_id.student_id.faculty_id
		level_id = self.fees_line_id.student_id.level_id
		semester_id = self.fees_line_id.student_id.semester_id

		
		if not partner_id.property_account_receivable_id or not partner_id.property_account_payable_id:
			msg = "Please configure account receivable for this partner"
			raise Warning(
				 _(msg)
				)

		if not self.fees_line_id.student_id.level_id and not self.fees_line_id.student_id.semester_id:

			level_id, semester_id = self.get_first_level(self.student_id)
			if not level_id or not semester_id:
				msg = "Please create level and semesters for "+self.student_id.faculty_id.name
				raise Warning(
				 _(msg)
				)

			# seq = self.env['ir.sequence'].next_by_code(
			# 'post.student.payment') or '/'

			faculty_code = self.fees_line_id.student_id.faculty_id.id
			year_order = self.fees_line_id.student_id.admission_rec.year_id.order
			#std_index = (self.fees_line_id.student_id.faculty_id.last_std_no)+1


			if not faculty_code:
				msg = "Please configure Faculty code"
				raise Warning(
				 _(msg)
				)		
			if not year_order:
				msg = "Please configure Academic Year"
				raise Warning(
				 _(msg)
				)
			code = year_order + str(faculty_code) # + str(std_index)
			self.fees_line_id.student_id.write({
			'state': 'registered',
			'level_id': level_id.id  ,
			'semester_id': semester_id.id ,
			'admission_date': fields.Date.today(),
			# 'index_id' : code,
			})
			
			# self.fees_line_id.student_id.faculty_id.write({
			# 'last_std_no' : std_index,
			# })

			self.fees_line_id.student_id.admission_rec.write({
				'state' : 'reg_form',
				})
			
		self.fees_line_id.write({
		    'paid_amount': paid_amount,
		    'paid': True if paid_amount == self.fees_line_id.sub_total else False ,
		    'payment_date': datetime.now(),
		    'residual_amount': self.fees_line_id.sub_total - paid_amount
		})


		self.create_payment_line(self.fees_line_id.student_id,self.amount,self.fees_line_id.student_id.level_id , self.fees_line_id.student_id.semester_id  , self.payment_type , self.check_number , self.account_number , self.currency_id , self.fees_line_id )
		return True


	def create_payment(self,partner_id):
		print('----------- create_payment')
		# payment_method_id = self.env['account.payment.method'].search([('payment_type' ,'=' , 'inbound')] ,limit=1)
		# invoice_id = self.env['account.invoice'].with_context(active_test=False).search([('id', '=', self.fees_line_id.invoice_id.id)])
		# payment_id = self.env['account.payment'].create({
		# 		'invoice_ids':[(6, 0, invoice_id.ids)],
		# 		'amount' : self.amount,
		# 		'currency_id' :self.currency_id.id,
		# 		'journal_id':self.journal_id.id,
		# 		'payment_date' : datetime.now(),
		# 		'payment_method_id' :  payment_method_id.id,
		# 		'payment_type' : 'inbound',
		# 		'partner_id' : partner_id.id,
		# 		'partner_type' : 'customer',
		# 		'state' : 'draft',
		# 		})
		# payment_id.action_validate_invoice_payment()

	def create_payment_line(self ,student_id, paid_amount ,level_id , semester_id , payment_type , check_number , account_number , currency_id , fees_line_id):
		print('------- in create_payment_line')
		# self.env['fees.payment.line'].create({
		# 	'student_id' : student_id.id,
		# 	'amount' : paid_amount,
		# 	'payment_date' : datetime.now(),
		# 	'level_id' : level_id.id,
		# 	'semester_id' : semester_id.id,
		# 	'payment_type' : payment_type ,
		# 	'check_number' : check_number ,
		# 	'account_number' : account_number ,
		# 	'fees_id' : fees_line_id.id ,
		# 	})


