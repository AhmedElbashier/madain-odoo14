from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class Student(models.Model):
	_inherit = 'uni.student'


	def calc_total_residaul(self):
		return sum (line.sub_total - line.paid_amount  for line in self.fees_ids if line.paid_amount != 0)
	
	year_id = fields.Many2one(
		string="Academic Year",
		comodel_name="uni.year",
		related='batch_id.academic_year_id'
		
	)
	nationality_type_id = fields.Many2one(
		comodel_name='uni.nationality.type',
		string='Nationality Type',
	)
	#currency_id = fields.Many2one('res.currency' , string="Currency")
	admission_year = fields.Many2one('uni.year', readonly=True)
	admission_rec = fields.Many2one('uni.admission', string="Admission Record")
	category_id = fields.Many2many(
		string="Discount Type",
		comodel_name="uni.student_category",
		readonly=True,
	)
	fees_ids = fields.One2many(
		string="Student Fees",
		comodel_name="student.fees",
		inverse_name="student_id",
		readonly=False
	)

	amount_sub_total = fields.Float(
		string='Sub Total', store=True, readonly=True, compute='_compute_amount')
	amount_total = fields.Float(
		string='Total', store=True, readonly=True, compute='_compute_amount')
	discount = fields.Float(
		string='Discount', store=True, readonly=True, compute='_compute_amount')
	
	scondary_certificate_id_img = fields.Binary(string="Secondary certificate Image", )
	student_national_id_img = fields.Binary(string="National ID Image", )
	student_passport_id_img = fields.Binary(string="Passport Image", )

	registration_status = fields.Selection(string='Registration Status',
		selection=[('registered','Registered'),
		('not_registered','Not Registerd')],
		default='not_registered')

	type_admission = fields.Selection(
		selection=[
			('new_admission', 'New Admission'),
			('transfer' , 'Transfer'),
			('bridging' , 'Bridging'),
			('academic_degree_holders','Academic Degree Holders'),
			('mature' , 'Mature'),
			
		],default='new_admission',string='Admission Type'
	)

	identity_type_id = fields.Many2one('uni.identity.type')
	identity_num = fields.Char('Identity Number')
	institution_name = fields.Char()
	study_years = fields.Char()
	study_college = fields.Char()
	study_join_year = fields.Char()
	study_cirtificate_type = fields.Char()

	first_registration = fields.Date()
	tuition_fees = fields.Monetary('Tuition Fees', required=True, currency_field='currency_id')
	registration_fees = fields.Monetary('Registration Fees', required=True, currency_field='currency_id')
	currency_id = fields.Many2one('res.currency', related='nationality_type_id.currency_id')
	register_id = fields.Many2one('uni.registration.record')
	external = fields.Boolean('External Student',default=False)

	@api.constrains("university_id")
	def _check_university_id(self):
		for record in self:
			if record.university_id:
				student_id = self.search([('university_id','=ilike',record.university_id),('admission_year','=',record.admission_year.id),('id','!=',record.id)])
				if student_id:
					raise ValidationError(_("There is another student in the same year hane a same number: %s" % student_id.name))
						
	
	@api.depends('fees_ids.sub_total', 'fees_ids.discount')
	def _compute_amount(self):
		for rec in self:
			rec.amount_sub_total = sum(
				line.sub_total for line in rec.fees_ids)
			rec.discount = sum(
				line.discount for line in rec.fees_ids)
			rec.amount_total = rec.amount_sub_total  # - self.discount


	def create_move(self):
		return {
			'name': _('Fees Payment'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'post.customer.check.action',
			'type': 'ir.actions.act_window',
			'target':'new',
			'context':{
				'default_name':self.check_number,
				'default_partner_id':self.line_id.partner_id.id,
				'default_amount': self.amount - self.paid_amount,
				'default_line_id':self.id,
				'default_description':self.description,
				'default_currency_id':self.currency_id.id,
				}

		}

class Guradians(models.Model):
    _inherit = 'uni.student.guradian'

    admission_id = fields.Many2one('uni.admission')

    identity_type_id = fields.Many2one('uni.identity.type')
    
    identity_num = fields.Char('Identity Number')


class GuradiansContact(models.Model):
    _inherit = 'guradian.contact'

    admission_id = fields.Many2one('uni.admission')


class Groups(models.Model):
    _inherit = 'uni.student.groups'

    academic_year_id = fields.Many2one('uni.year', required=True)


