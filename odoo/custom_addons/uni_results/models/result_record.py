
from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Result(models.Model):
	_name = 'uni.result.record'
	_inherit = ['mail.thread']

	name = fields.Char(
		required=True,
		string='Name'
	)
	exam_id = fields.Many2one(
		'uni.exam.record',
		string='Exam Record',
		domain=[('state','=','done')]
	)
	year_id = fields.Many2one(
		'uni.year',
		string='Academic Year',
	)

	level_id = fields.Many2one(
		'uni.faculty.level',
		string='Level',
	)

	semester_id = fields.Many2one(
		'uni.faculty.semester',
		string="Term",
	)

	batch_id = fields.Many2one(
		'uni.faculty.department.batch',
		string='Batch',
	)

	exam_type_id = fields.Many2one(
		'uni.exam.types', 
		required=True
	)

	program_council_meet_date = fields.Date(readonly=True)
	scientific_council_meet_date = fields.Date(readonly=True)
	result_confirm_date = fields.Date(readonly=True)
	result_advertisement_date = fields.Date()

	marksheet_id = fields.Many2one(
        'marksheet.register', 'Marksheet')

	marksheet_line = fields.One2many(
        'marksheet.line', 'result_id', 'Marksheet',compute="get_marksheet_lines")

	std_recommendation_ids = fields.One2many(
		'student.recommendations.list',
		'result_id'
	)

	subj_recommendation_ids = fields.One2many(
		'subject.recommendations.list',
		'result_id',
	)

	recorrection_recommendation_ids = fields.One2many(
		'student.recommendations.list',
		'recorrection_result_id',
	)

	subject_ids = fields.Many2many(
		'uni.faculty.subject',related="exam_id.subject_ids")
	students = fields.Many2many('uni.student',related="exam_id.students")
	state = fields.Selection(
		selection=[
			('draft','Draft'),
			('confirm','Confirmed'),
			('program_council','Program Council'),
			('program_council_recomm','program Council Recommendations'),
			('scientific_council','Scientific Council'),
			('scientific_council_recomm','Scientific Council Recommendations'),
			('close','Closed'),
			('recorrection_period','Recorrection Period'),
			('recorrection_recomm','Recorrection Recommendations'),
			('done','Done'),
		],default="draft")

	end_level = fields.Boolean('End of Academic Level ?',related='exam_id.end_level')

	company_id = fields.Many2one(
		comodel_name='res.company',
		default=lambda self: self.env.user.company_id
	)

	_sql_constraints = [
	   ('unique_result_record', 'unique (year_id , level_id , semester_id , batch_id , exam_type_id)',
	   "Sorry.. They are already a Result Record for this level in this academic year")
	]

	@api.onchange('exam_id')
	def get_data(self):
		for rec in self:
			if rec.exam_id:
				rec.exam_type_id = rec.exam_id.exam_type
				rec.year_id = rec.exam_id.academic_year_id
				rec.level_id = rec.exam_id.level_id
				rec.semester_id = rec.exam_id.semester_id
				rec.batch_id = rec.exam_id.batch_id
				rec.end_level = rec.exam_id.end_level
				rec.marksheet_id = self.env['marksheet.register'].search([
					('exam_id','=',rec.exam_id.id)],limit=1).id

	@api.depends('marksheet_id')
	def get_marksheet_lines(self):
		for rec in self:
			if rec.marksheet_id:
				rec.marksheet_line = rec.marksheet_id.marksheet_line
			else:
				rec.marksheet_line = False

	
	def to_confirm(self):
		self.result_confirm_date = fields.Date.today()
		self.state = 'confirm'

	def to_program_council(self):
		self.state = 'program_council'

	def to_program_council_rec(self):
		self.state = 'program_council_recomm'

	def to_scientific_council(self):
		for result in self:
			for rec in result.subj_recommendation_ids:
				attendees_ids = self.env['exam.attendees'].search([('exam_id.record_id','=',result.exam_id.id),('subject','=',rec.subject_id.id),('final_degree','>=',rec.minimum_degree),('final_degree','<',rec.minimum_degree+rec.extra_degree)])
				for attendee in attendees_ids:
					if rec.absolute:
						attendee.program_council_push = rec.extra_degree
					else:
						#if attendee.final_degree <= rec.minimum_degree and attendee.final_degree > 0:
						attendee.program_council_push = rec.minimum_degree+rec.extra_degree - attendee.final_degree
						# else:
						# 	attendee.program_council_push = 0

			for rec in result.std_recommendation_ids:
				attendees_ids = self.env['exam.attendees'].search([('exam_id.record_id','=',result.exam_id.id),('student_id','=',rec.student_id.id),('subject','=',rec.subject_id.id)])
				for attendee in attendees_ids:
					attendee.program_council_student_push =  rec.given_degree
			result.program_council_meet_date = fields.Date.today()
			result.state = 'scientific_council'

	def to_scientific_council_rec(self):
		self.state = 'scientific_council_recomm'

	def to_close(self):
		subj_recommendation_ids = self.subj_recommendation_ids.search([('result_id','=',self.id),('recommenation_type','=','scientific_council')])
		std_recommendation_ids = self.std_recommendation_ids.search([('result_id','=',self.id),('recommenation_type','=','scientific_council')])
		for rec in subj_recommendation_ids:
			attendees_ids = self.env['exam.attendees'].search([('exam_id.record_id','=',self.exam_id.id),('subject','=',rec.subject_id.id),('subject_total_degree','>=',rec.minimum_degree),('subject_total_degree','<',rec.minimum_degree+rec.extra_degree)])
			for attendee in attendees_ids:
				if rec.absolute:
					attendee.scientific_council_push = rec.extra_degree
				else:
					#if attendee.final_degree <= rec.minimum_degree and attendee.final_degree > 0:
					attendee.scientific_council_push = rec.minimum_degree+rec.extra_degree - attendee.final_degree
					# else:
					# 	attendee.scientific_council_push = 0

		for rec in std_recommendation_ids:
			attendees_ids = self.env['exam.attendees'].search([('exam_id.record_id','=',self.exam_id.id),('student_id','=',rec.student_id.id),('subject','=',rec.subject_id.id)])
			for attendee in attendees_ids:
				attendee.scientific_council_student_push =  rec.given_degree
		self.scientific_council_meet_date = fields.Date.today()

		if not self.end_level:
			if self.exam_type_id.exam_category == 'first_round' and not self.exam_type_id.is_substitutionals:
				semester_id = self.env['uni.faculty.semester'].search([
					('order','=',str(int(self.batch_id.semester_id.order)+1))],limit=1) 
				if not semester_id:
					raise ValidationError(_('Term %s'%(int(self.batch_id.semester_id.order)+1)+' is not configure, Please make sure that the term for the batch is set correctly'))

				self.batch_id.semester_id = semester_id
		else:
			if self.exam_id.exam_type.is_substitutionals:
				self.batch_id.write({
					'next_level_id': self.env['uni.faculty.level'].search([
								('order','=',str(int(self.batch_id.level_id.order)+1))],limit=1).id,
					})
			elif self.exam_id.exam_type.exam_category == 'first_round':
				exam_ids = self.env['exam.exam'].search([('record_id','=',self.exam_id.id)]).ids
				attendees_ids = self.env['exam.attendees'].search([('exam_id','in',exam_ids),('status','=','justified_absence')])
				if not attendees_ids:
					self.batch_id.write({
					'next_level_id': self.env['uni.faculty.level'].search([
								('order','=',str(int(self.batch_id.level_id.order)+1))],limit=1).id,
					})

		self._get_student_academic_status()

		self.state = 'close'

	def result_advertisement(self):
		self.result_advertisement_date = date.today()
		recorrection_period = self.company_id.recorrection_period
		if recorrection_period <= 0:
			raise ValidationError(_('Please Configure The Recorrection Period Days From Setting'))

		self.state = 'recorrection_period'

	def start_recorrection(self):
		self.state = 'recorrection_period'

	def recorrection_recomm(self):
		self.state = 'recorrection_recomm'


	def rest_draft(self):
		self.state = 'draft'

	def action_done(self):
		for rec in self.recorrection_recommendation_ids:
				attendees_ids = self.env['exam.attendees'].search([('exam_id.record_id','=',self.exam_id.id),('student_id','=',rec.student_id.id),('subject','=',rec.recorrection_subject_id.id)])
				for attendee in attendees_ids:
					attendee.recorrection_push =  (rec.given_degree-attendee.final_degree)
		self.state = 'done'

	def check_recorrection_period(self):
		result_record_ids = self.search([('state','=','recorrection_period')])
		for rec in result_record_ids:
			recorrection_period = rec.company_id.recorrection_period
			if rec.result_advertisement_date:
				end_date = rec.result_advertisement_date + timedelta(days=recorrection_period)  
				if date.today() > end_date :
					rec.state = 'recorrection_recomm'


	def _get_student_academic_status(self):
		request_ids = self.env['uni.discount_scholarship.request']
		for line in self.marksheet_line:
			if not self.end_level:
				line.student_id.semester_id = self.env['uni.faculty.semester'].search([
					('order','=',str(int(line.semester_id.order)+1))],limit=1)
			else:
				if line.status == 'pass':
					line.student_id.write({
						'academic_status': 'success',
						# 'level_id': self.env['uni.faculty.level'].search([
						# 			('order','=',str(int(line.student_id.level_id.order)+1))],limit=1).id,
						# 'semester_id': self.env['uni.faculty.semester'].search([
						# 			('order','=','1')],limit=1).id
						})
					line.academic_status = 'success'
				elif line.status == 'supplement':
					line.student_id.write({
						'academic_status': 'supplement'})
					line.academic_status = 'supplement'
				elif line.status == 'substitution':
					line.student_id.write({
						'academic_status': 'substitution'})
					line.academic_status = 'substitution'
				elif line.status == 'substitutional_supplement':
					line.student_id.write({
						'academic_status': 'substitutional_supplement'})
					line.academic_status = 'substitutional_supplement'
				elif line.status == 'repeat':
					request_ids = self.env['uni.discount_scholarship.request'].search([('student_id','=',line.student_id.id),('state','=','approved')])
					line.student_id.write({
						'academic_status': 'repeat'})
					line.academic_status = 'repeat'
				elif line.status == 'repeat_subjects':
					request_ids = self.env['uni.discount_scholarship.request'].search([('student_id','=',line.student_id.id),('state','=','approved')])
					line.student_id.write({
						'academic_status': 'repeat_subjects'})
					line.academic_status = 'repeat_subjects'
				elif line.status == 'dismiss':
					line.student_id.write({
						'academic_status': 'dismiss',
						'state': 'dismissed'})
					line.academic_status = 'dismiss'

				if request_ids:
					for request in request_ids:
						request.write({'state':'closed','end_date':date.today()})
	