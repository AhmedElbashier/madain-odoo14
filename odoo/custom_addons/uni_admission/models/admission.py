from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.uni_core.utils import get_default_faculty
from datetime import datetime, timedelta,date
import random
from odoo.exceptions import ValidationError


class Admission(models.Model):
	_name = "uni.admission"
	_inherit = ['mail.thread']
	_rec_name = "name"

	def get_current_admission_year(self):
		return self.env['uni.year'].search([('state','=','approved'),('active','=',True)], order='id desc')[0].id


	active = fields.Boolean(default=True)

	date = fields.Date(
		string="Date", default=fields.Date.today(), readonly=True)
	
	student_id = fields.Many2one('uni.student')
	
	first_name = fields.Char(string='First name')
	
	middle_name = fields.Char(string='Middle name')
	
	last_name = fields.Char(string='Last name')
	
	fourth_name = fields.Char(string='Fourth name')
	# English
	
	first_name_en = fields.Char(string='First name (English)')
	
	middle_name_en = fields.Char(string='Middle name (English)')
	
	last_name_en = fields.Char(string='Last name (English)')
	
	fourth_name_en = fields.Char(string='Fourth name (English)')


	name = fields.Char(
		string='Name',
		compute='_compute_name',
		store=True,
		index=True
	)
	admission_std_number = fields.Char('Admission Number')

	university_id = fields.Char(
		string='University ID',
		store=True
	)

	university_login = fields.Char(readonly=True)

	program_id = fields.Many2one(
		'uni.faculty.program',
		string='Program',
		store=True
	)

	secondary_school = fields.Many2one('uni.school', string='Secondary School')
	
	school_percentage = fields.Char()

	nationality_type_id = fields.Many2one(
		comodel_name='uni.nationality.type',
		string='Nationality Type',
		store=True,
	)

	acadimic_year_id = fields.Many2one(
		string="Academic Year",
		comodel_name="uni.year",
		default =get_current_admission_year,
		domain="[('active','=',True)]",
	)

	state = fields.Selection(
		string="State",
		selection=[
			('draft', 'Draft'),
			('candidate', 'Candidate'),
			('wait_interview', 'Wait For Interview'),
			('interview' , 'Interview'),
			('accepted', 'Accepted'),
			('registered', 'First Registration'),
			('rejected', 'Rejected'),
		],
		default='draft',
	)

	batch_id = fields.Many2one(
		string="Batch",
		comodel_name="uni.faculty.department.batch",
	)

	level_id = fields.Many2one(
		string="Level",
		comodel_name="uni.faculty.level",
		related="batch_id.level_id"
	)

	faculty_id = fields.Many2one(
		'res.company',
		string='Faculty',
		store=True
	)

	user_id = fields.Many2one(
		comodel_name='res.users',
		ondelete="restrict",
		readonly=True,
		index=True
	)
	type_admission = fields.Selection(
		selection=[
			('new_admission', 'New Admission'),
			('transfer' , 'Transfer'),
			('bridging' , 'Bridging'),
			('academic_degree_holders','Academic Degree Holders'),
			('mature' , 'Mature'),
			
		],default='new_admission',string='Admission Type'
	)
	gender = fields.Selection(
		string='Gender',
		selection=[
			('male', 'Male'),
			('female', 'Female')
		]
	)
	nationality_id = fields.Many2one(
		comodel_name='res.country',
		string='Nationality'
	)

	sudan_country_id = fields.Boolean(compute='compute_country_id')

	religion = fields.Selection(string='Religion', selection=[
		('islam', 'Islam'),
		('christianity', 'Christianity'),
		('other', 'Other')
	])
	city = fields.Selection([('kh','Khartoum'),
	                         ('ba','Baharey'),
							 ('om','Oumdorman')])
	
	std_img = fields.Binary(string="Student Image", )

	contact_ids = fields.One2many('guradian.contact','admission_id')
	
	phone = fields.Char(string='Phone(1)')
	
	mobile = fields.Char(string='Phone(2)')
	
	email = fields.Char()
	
	address = fields.Char(string="Address")

	scondary_certificate_id_img = fields.Binary(string="Secondary certificate Image", )
	
	student_national_id_img = fields.Binary(string="National ID Image", )
	
	student_passport_id_img = fields.Binary(string="Passport Image", )
	
	medical_condition = fields.Selection(
		string="Medical Check",
		selection=[
			('fit', 'fit'),
			('unfit', 'unfit'),
		],
		default="fit",
	)

	committee_head = fields.Char('Head of Committee')
	
	committee_notes = fields.Text(string="Notes", )
	
	committee_recom = fields.Selection(
		string="Committee Recommendation",
		selection=[
			('accepted', 'Acceptable'),
			('not_accepted', 'Not Acceptable'),
		],
		default="accepted",
	)

	year_id = fields.Many2one(
		string="Academic Year",
		comodel_name="uni.year",
		related='acadimic_year_id',
		readonly=True,
	)
	
	birth_date = fields.Date(string='Birth date')

	place_of_birth = fields.Char(string='Place of Birth')

	gender = fields.Selection(
		string='Gender',
		selection=[
			('male', 'Male'),
			('female', 'Female')
		]
	)
	
	religion = fields.Selection(string='Religion', selection=[
		('islam', 'Islam'),
		('christianity', 'Christianity'),
		('other', 'Other')
	])
	
	category_id = fields.Many2many(
		string="Discount Type",
		comodel_name="uni.student_category",
	)

	medical_data = fields.Many2one(
		string="Medical Data",
		comodel_name="uni.health_service.medical_data",
	)

	fees_ids = fields.One2many(
		string="Student Fees",
		comodel_name="student.fees",
		inverse_name="student_id",
		readonly=True,
		# related='student_id.fees_ids',
	)
	
	std_number = fields.Char(
		string='Student Number',
		readonly=True
		)

	identity_type_id = fields.Many2one('uni.identity.type')
	
	identity_num = fields.Char('Identity Number')
	
	institution_name = fields.Char()
	
	study_years = fields.Char()
	
	study_college = fields.Char()
	
	study_join_year = fields.Char()
	
	study_cirtificate_type = fields.Char()

	is_installment = fields.Boolean(string="Installment")

	add_fees = fields.Many2many('uni.add_fees' , string="Additional Fees")

	guardians_ids = fields.One2many('uni.student.guradian','admission_id',string="Guardians")

	batch_counter = fields.Integer()
	
	admission_year = fields.Many2one('uni.year', string='Admission Year',related='acadimic_year_id')
	
	register_id = fields.Many2one('uni.registration.record')
	
	admission_record_id = fields.Many2one('uni.admission.record')
	
	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)
	
	admission_steps_ids = fields.One2many('admission.steps.directions', related='company_id.admission_steps_ids')
	
	registration_steps_ids = fields.One2many('registration.steps.directions', related='company_id.registration_steps_ids')
	
	guidelines_financial_management  = fields.One2many('guidelines.financial.management', related='company_id.guidelines_financial_management')
	
	language = fields.Many2one('res.lang',string='Candidate Language')
	
	fulfillment_subject = fields.Boolean()
	
	fulfillment_subject_id = fields.One2many('uni.admission.fulfillment.subject', 'admission_id')


	@api.constrains('university_id')
	def _check_name(self):
		for record in self:
			if record.university_id:
				admission_id = self.env['uni.admission'].search([('university_id','=ilike',record.university_id),('acadimic_year_id','=',record.acadimic_year_id.id),('id','!=',record.id)])
				if admission_id:
					raise ValidationError(_("There is another student with the same university number in this year"))

	@api.constrains('batch_id')
	def _check_batch_id(self):
		for record in self:
			if record.type_admission != 'new_admission' and record.batch_id:
				registration_record_id = self.env['uni.registration.record'].search([('level_id','=',record.level_id.id),('academic_year_id','=',record.acadimic_year_id.id),('state','!=','approved')])
				if registration_record_id:
					raise ValidationError(_('There is no registration record opened for this batch'))

	@api.onchange('acadimic_year_id')
	def onchange_academic_year(self):
		domain = {}
		programs = [program.id for program in self.acadimic_year_id.program_ids]
		domain = {
				'domain':{
					'program_id':[('id','in',programs)],
				}
			}
		if self.acadimic_year_id:
			admission_record_id = self.env['uni.admission.record'].search([('academic_year_id','=',self.acadimic_year_id.id),('state','=','approved')],limit=1)
			if admission_record_id:
				self.admission_record_id = admission_record_id.id
			else:
				raise ValidationError(_("There is no approved admission record in the new admission year"))


		return domain
	@api.depends('first_name', 'middle_name', 'last_name', 'fourth_name')
	def _compute_name(self):
		for record in self:
			record.name = '%s %s %s %s' % (
				record.first_name,
				record.middle_name,
				record.last_name,
				record.fourth_name,
			)

	@api.depends('nationality_id')
	def compute_country_id(self):
		for rec in self:
			rec.sudan_country_id = (rec.nationality_id.id == self.env.ref("base.sd").id)

			
	@api.constrains('university_id')
	def check_university_id(self):
		if not self.university_id:
			self.university_login = random.randint(0, 5000)
			
	@api.onchange('program_id','type_admission')
	def set_batch(self):
		if self.program_id and self.type_admission:
			domain= {}
			batch_ids = self.env['uni.faculty.department.batch'].search([])
			batch_id = max(batch_ids.search([('program_id','=',self.program_id.id)]).ids)
			if batch_ids:
				self.batch_id = batch_id
				if self.type_admission == 'new_admission':
					domain = {
					'domain':{
						'batch_id':[('id','=',batch_id)],
						}
					}					
				else:
					domain = {
					'domain':{
						'batch_id':[('program_id','=',self.program_id.id)],
						}
					}
				return domain
			else:
				raise ValidationError(_('No batch under this program'))


	def get_first_level(self):
		level = self.env['uni.faculty.level'].search(
			 [],limit=1, order="order asc")
		semester = self.env['uni.faculty.semester'].search(
			 [],limit=1, order="order asc")
		return level, semester


	def to_candidate(self):
		if not self.user_id:
			candidate_std_partner = self.env['res.partner'].create({
				'name': self.name,
				'display_name': self.name,
				'active': True,
				# 'customer_rank': 1,
				})

			candidate_std_user = self.env['res.users'].create({
				'login': self.university_id if self.university_id else self.university_login,
				'password': self.university_id if self.university_id else self.university_login,
				'partner_id': candidate_std_partner.id,
				}) 
			
			self.user_id = candidate_std_user.id
		 
		return self.write({'state': 'candidate'})

	def to_wait_interview(self):
		self.write({'state': 'wait_interview'})

	def to_interview(self):
		self.write({'state': 'interview'})

	def to_accepted(self):
		self.write({'state': 'accepted'})

	def to_rejected(self):
		# partner_id = self.user_id.partner_id
		# self.user_id.unlink()
		# partner_id.unlink()
		self.write({'state': 'rejected'})

	def to_return(self):
		self.write({'state': 'interview'})

	def to_draft(self):
		self.write({'state': 'draft'})

	def create_student_discount(self,student):
		discount_request_ids = self.env['uni.discount_scholarship.request'].search([('type','=','candidate'),('candidate_id','=',self.id)])
		if discount_request_ids:
			for request in discount_request_ids:
				request_id = self.env['uni.discount_scholarship.request'].create({
					'type':'student',
					'type_of_dis':request.type_of_dis,
					'discount_to':request.discount_to,
					'student_id':student.id,
					'academic_year_id':request.academic_year_id.id,
					'admission_year_id':request.admission_year_id.id,
					'discount_scholarship_id':request.discount_scholarship_id.id,
					'start_date':request.start_date,
					'end_date':request.end_date,
					'sibling_status':request.sibling_status,
					'sibling_student_id':request.sibling_student_id.id,
					'sibling_candidate_id':request.sibling_candidate_id.id,
					'second_sibling':request.second_sibling,
					'first_brother_percentage':request.first_brother_percentage,
					'second_brother_percentage':request.second_brother_percentage,
					'fees_amount':request.fees_amount,
					'discounted_amount':request.discounted_amount,
					'total_amount':request.total_amount,
					'guardian_name':request.guardian_name.id,
					'percentage':request.percentage,
					'certificate_info':request.certificate_info,
					'program_id':[(6,0,request.program_id.ids)],
					'state':request.state,
					})
				#request.unlink()
				request.write({'active':False})

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

	def action_create_invoice(self,request_id):
		registration_fees_account_id = self.company_id.registration_fees_account_id.id
		tuition_fees_account_id = self.company_id.tuition_fees_account_id.id
		journal_id = self.company_id.journal_id.id

		if not registration_fees_account_id or not tuition_fees_account_id or not journal_id:
			raise ValidationError(_("Please Configure The Accounting Fees Information From Setting"))

		invoice_line_values = [([0,0,{'name':'Tuition Fees','account_id':tuition_fees_account_id,'price_unit':request_id.tuition_fees}])]
		invoice_line_values.append([0,0,{'name':'Registration Fees','account_id':registration_fees_account_id,'price_unit':request_id.registration_fees}])
		invoice_id = self.env['account.move'].create({
			'partner_id':request_id.student_id.partner_id.id,
			'invoice_date':date.today(),
			'move_type':'out_invoice',
			'journal_id':journal_id,
			'currency_id':request_id.currency_id.id,
			'invoice_line_ids':invoice_line_values,
			})
		invoice_id.action_post()
		request_id.invoice_id = invoice_id.id

	def create_student_invoice(self,request_id):
		dates = [installment.start_date for installment in request_id.fees_installment_ids]
		if dates:
			start_date = min(dates)
			installment_id = self.env['uni.fees.installment'].search([('registration_request_id','=',request_id.id),('start_date','=',start_date)],order="first_installment desc",limit=1)
			if installment_id:
				installment_id.action_create_invoice()

	def calculate_student_fees(self):
		fees = 0.0
		tuition_fees = 0.0
		tuition_fees_id = self.env['uni.program.fees'].search([('program_id','=',self.program_id.id),('year_id','=',self.acadimic_year_id.id),('nationality_type_id','=',self.nationality_type_id.id)],limit=1)
		registration_fees = self.env['uni.registered.fees'].search([('year_id','=',self.acadimic_year_id.id),('nationality_type_id','=',self.nationality_type_id.id)],limit=1).registration_fees
		
		if self.type_admission == 'new_admission':
			if tuition_fees_id.add_new == 0.0:
				raise ValidationError(
					_("Please Configure The New Admission Fees")
				)
			tuition_fees = 	tuition_fees_id.add_new

		elif self.type_admission == 'mature':
			if tuition_fees_id.mature == 0.0:
				raise ValidationError(
					_("Please Configure The Mature Fees")
				)
			tuition_fees = 	tuition_fees_id.mature

		elif self.type_admission == 'transfer':
			if tuition_fees_id.transference == 0.0:
				raise ValidationError(
					_("Please Configure The Transference Fees")
				)
			tuition_fees = 	tuition_fees_id.transference

		elif self.type_admission == 'bridging':
			if tuition_fees_id.academic_degrees == 0.0:
				raise ValidationError(
					_("Please Configure The Bridging Fees")
				)
			tuition_fees = 	tuition_fees_id.academic_degrees
		
		return tuition_fees,registration_fees
		

	def create_registration_request(self,student):
		request_id = self.env['uni.registration.request']
		registration_record_id = self.env['uni.registration.record']
		if self.type_admission == 'new_admission':
			registration_record_id = self.env['uni.registration.record'].search([('academic_year_id','=',self.acadimic_year_id.id),('level_id.order','=','1')])
		else:
			registration_record_id = self.env['uni.registration.record'].search([('academic_year_id','=',self.acadimic_year_id.id),('level_id','=',self.level_id.id)])

		print('---------------------- registration',registration_record_id,student.year_id.name , registration_record_id.state)
		if not registration_record_id:
			raise ValidationError(_('There is no registration record'))
		elif registration_record_id.state != 'approved':
			raise ValidationError(_('The registration record does not approved'))

		installment = []
		tuition_fees,registration_fees = self.calculate_student_fees()
		student.write({'tuition_fees':tuition_fees,'registration_fees':registration_fees})
		percentage,discount_amount,discount_record = self.check_student_discounts(student)
		program_registration_id = self.env['uni.program.registration'].search([('registration_id','=',registration_record_id.id),('batch_id','=',student.batch_id.id)])
		if self.acadimic_year_id.allow_installment:
			for fees in program_registration_id.installment_ids:
				installment.append([0,0,{'name':fees.name,
										'installment_percentage':tuition_fees*fees.installment_percentage/100,
										'discount_amount':discount_amount,
										'start_date':fees.start_date,
										'end_date':fees.end_date,
										'first_installment':fees.first_installment,
										'include_registration_fees':fees.include_registration_fees,
										}])
		else:
			installment.append([0,0,{'name':'1',
					'installment_percentage':tuition_fees,
					'discount_amount':discount_amount,
					'start_date':self.acadimic_year_id.start_date,
					'end_date':self.acadimic_year_id.end_date,
					'first_installment':True,
					'include_registration_fees':True,
					}])
		request_id = self.env['uni.registration.request'].create({
			'student_id':student.id,
			'academic_year_id':self.acadimic_year_id.id,
			'admission_year_id':self.admission_year.id,
			'program_id':student.program_id.id,
			'level_id':student.level_id.id,
			'semester_id':student.semester_id.id,
			'state':'draft',
			'tuition_fees':tuition_fees,
			'registration_fees':registration_fees,
			'fees_installment_ids':installment,
			'batch_id':self.batch_id.id,
			'discount_perc':percentage,
			'discounted_amount':discount_amount,
			'total_amount':(tuition_fees-discount_amount),
			'discount_record':discount_record.id,
			'state':'approved',
			})
		self.create_student_invoice(request_id)

	
	def create_student_record(self):
		# create student record
		# generate std_number
		if self.type_admission != 'new_admission' and self.fulfillment_subject and not self.fulfillment_subject_id:
			raise ValidationError(_('You must enter one subject at least in fulfillment subject line.'))
		batch_students = self.env['uni.student'].search([('batch_id','=',self.batch_id.id)]).ids
		counter = len(batch_students) if batch_students else 0
		self.std_number = str(self.batch_id.code)+ '-' + str(counter + 1).zfill(3)

		level,semester = self.get_first_level()

		student_id = self.env['uni.student'].create({
			'first_name': self.first_name,
			'middle_name': self.middle_name,
			'last_name': self.last_name,
			'fourth_name': self.fourth_name,
			'first_name_en': self.first_name_en,
			'middle_name_en':self.middle_name_en,
			'last_name_en': self.last_name_en,
			'fourth_name_en': self.fourth_name_en,
			'university_id':self.university_id,
			'std_number':self.std_number,
			'program_id':self.program_id.id,
			'level_id':level.id if self.type_admission == 'new_admission' else self.level_id.id,
			'semester_id':semester.id if self.type_admission == 'new_admission' else self.batch_id.semester_id.id,
			'type_admission': self.type_admission,
			'birth_date': self.birth_date,
			'place_of_birth': self.place_of_birth,
			'nationality_id': self.nationality_id.id,
			'gender': self.gender,
			'address': self.address,
			'city': self.city,
			'email': self.email,
			'religion': self.religion,
			'identity_type_id': self.identity_type_id.id,
			'identity_num': self.identity_num,
			'student_national_id_img': self.student_national_id_img,
			'student_passport_id_img': self.student_passport_id_img,
			'scondary_certificate_id_img':self.scondary_certificate_id_img,
			'admission_year': self.acadimic_year_id.id,
			'year_id':self.acadimic_year_id.id,
			'school_percentage': self.school_percentage,
			'secondary_school': self.secondary_school.id,
			'institution_name': self.institution_name,
			'study_years': self.study_years,
			'study_college': self.study_college,
			'study_join_year': self.study_join_year,
			'study_cirtificate_type': self.study_cirtificate_type,
			'std_img':self.std_img,
			'partner_id': self.user_id.partner_id.id,
			'user_id':self.user_id.id,
			'admission_rec': self.id,
			'nationality_type_id': self.nationality_type_id.id,
			'medical_condition':self.medical_condition,
			'committee_recom':self.committee_recom,
			'committee_head':self.committee_head,
			'committee_notes':self.committee_notes,
			'batch_id':self.batch_id.id,
			'first_registration':date.today(),
			'state':'student',
			'tuition_fees':0.0,
			'registration_fees': 0.0

			})
		for guardian in self.guardians_ids:
			guardian.write({'student_id':student_id.id})
		for contact in self.contact_ids:
			contact.write({'student_id':student_id.id})
		self.create_student_discount(student_id)
		print('---------- student year',student_id.year_id.name)	
		self.create_registration_request(student_id)
		return self.write({'state': 'registered','student_id':student_id.id,'active':False})

	def create_move_line(self, move_id, account_id, partner_id, lable, debit, credit, date):
		self.env['account.move.line'].with_context({
			'check_move_validity': False
		}).create({
			'account_id': account_id,
			'name': lable,
			'debit': debit,
			'credit': credit,
			'date': date,
			'move_id': move_id,
			'partner_id': partner_id,
		})
	ref = None

	def create_move(self, amount, ref, journal_id, debit_account, credit_account, partner_id, date, lable, payment_id=False):
		move_id = self.env['account.move'].create({
			'journal_id': journal_id,
			'date': date,
			'ref': ref,
			'payment_id': payment_id,
		})
		# recivable
		self.create_move_line(move_id.id, debit_account, partner_id,
							  lable, amount, 0.0, date)
		# payment
		self.create_move_line(move_id.id, credit_account, partner_id,
							  lable, 0.0, amount, date)

		move_id.post()

	def create_payment(self, amount, currency):
		self.env['uofk.payment'].create({
			'reference': self.university_id,
			'name': self.name,
			# TODO: service must be generic
			'service': 1001,
			'currency': currency,
			'amount': amount,
		})

	def get_student_fees(self):
		dept_fees = self.env['uni.study_fees.departments'].search([
			# ('department_id', '=', self.department_id.id),
			('nationality_type_id', '=',
			 self.nationality_type_id.id),
			('year_id', '=', self.year_id.id),
			('state', '=', 'done')
		], limit=1)

		if not dept_fees:
			# No dept fees? let's try the global faculty fees
			faculty_fees = self.env['uni.study_fees.line'].search([
				('faculty_id', '=', self.faculty_id.id),
				('nationality_type_id', '=',
				 self.nationality_type_id.id),
				('year_id', '=', self.year_id.id), ('state', '=', 'done')
			], limit=1)

		return dept_fees or faculty_fees

	@api.model
	def create(self, values):
		batch_id = self.env['uni.faculty.department.batch'].browse(values['batch_id'])
		student_admission_id = self.search_count([('acadimic_year_id','=',values['acadimic_year_id'])])
		values['admission_std_number'] = str(batch_id.code)+ '-' + str(student_admission_id+1).zfill(3)

		admission_ids = self.search([])
		if admission_ids:
			last_admission_record = max(admission_ids)
			values['batch_counter'] = last_admission_record.batch_counter + 1
		else:
			values['batch_counter'] = 1
		return super(Admission, self).create(values)


	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError(_('The record must be in draft state to be deleted.'))
			else:
				return super(Admission, self).unlink()

class UniSchool(models.Model):
	_name = 'uni.school'

	name = fields.Char()