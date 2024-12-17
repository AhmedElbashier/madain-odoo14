
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpExamAttendees(models.Model):
	_name = "exam.attendees"
	_rec_name = "student_id"
	_description = "Exam Attendees"

	student_id = fields.Many2one('uni.student', 'Student', required=True)
	university_id = fields.Char(related='student_id.std_number', string='University ID')
	seeting_number = fields.Char('Setting Number')
	status = fields.Selection(
		[('presence', 'Presence'), ('absence', 'Absence'), ('justified_absence', 'Justified Absence')],
		'Status', default="presence")
	marks = fields.Integer('Marks')
	note = fields.Text('Note')
	exam_id = fields.Many2one(
		'exam.exam', 'Exam', required=True, ondelete="cascade")
	attendees_degree = fields.Float()
	practical_degree = fields.Float()
	year_work_degree = fields.Float()
	final_exam_degree = fields.Float()
	final_degree = fields.Float(compute="compute_final_degree")
	violation_id = fields.Many2many('violation.type')
	marksheet_line_id = fields.Many2one(
		'marksheet.line', 'Marksheet Line')
	subject = fields.Many2one('uni.faculty.subject',related='exam_id.subject_id')
	hour = fields.Integer(related='subject.credit_hours', string="Subject Hours")
	subject_degree_point = fields.Float(compute="_get_subject_points")
	subject_point = fields.Float(compute="_get_subject_points",string="Subject Points")
	subject_grade_letter = fields.Char('Grade in Letter', readonly=True, compute='_compute_subject_grade')
	subject_grade = fields.Char('Grade', readonly=True, compute='_compute_subject_grade')
	program_council_push = fields.Float('Program Council Subject Push')
	scientific_council_push = fields.Float('Scientific Council Subject Push')
	program_council_student_push = fields.Float('Program Council Student Push')
	scientific_council_student_push = fields.Float('Scientific Council Student Push')
	recorrection_push = fields.Float('Recorrection Push')
	subject_total_degree = fields.Float('Total Degree',compute="compute_total_subject_degree")
	subject_status = fields.Selection([
		('pass', 'Pass'),
		('fail', 'Fail'),
		('substitutional', 'Substitutional'),
		('deprived','Deprived'),
	], 'Status',compute='_compute_status',store=True)
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	main = fields.Boolean(default=True)

	def _compute_subject_grade(self):
		for rec in self:
			rec.subject_grade_letter = ''
			rec.subject_grade = ''
			grade = self.env['grade.conf']
			if rec.subject.subject_grade:
				grade = rec.subject.subject_grade
			elif rec.student_id.program_id.curriculum_id.subject_grade:
				grade = rec.student_id.program_id.curriculum_id.subject_grade
			elif rec.company_id.subject_grade:
				grade = rec.company_id.subject_grade
			else:
				raise ValidationError(_('Sorry you must configr the grade configuration'))

			for categ in grade.category_ids:
				if rec.subject_degree_point >= categ.minimum_degree and rec.subject_degree_point <= categ.maximum_degree:
					rec.subject_grade_letter = categ.grade_letter
					rec.subject_grade = categ.grade
				
			if rec.status == 'justified_absence' and not rec.exam_id.record_id.is_substitutionals:
				rec.subject_grade_letter = '-'
				rec.subject_grade = '-'

	@api.depends('final_degree','program_council_push','scientific_council_push','recorrection_push','program_council_student_push','scientific_council_student_push')
	def compute_total_subject_degree(self):
		for rec in self:
			rec.subject_total_degree = rec.final_degree+rec.scientific_council_push+rec.scientific_council_student_push+rec.program_council_push+rec.program_council_student_push+rec.recorrection_push


	@api.depends('subject_total_degree','exam_id.success_degree','final_degree')
	def _compute_status(self):
		for rec in self:
			if rec.subject_total_degree >= rec.exam_id.success_degree:
				rec.write({'subject_status':'pass'})
			if rec.subject_total_degree < rec.exam_id.success_degree:
				rec.write({'subject_status':'fail'})
			if rec.exam_id.record_id.exam_category == 'first_round' and not rec.exam_id.record_id.is_substitutionals:
				if rec.status == 'justified_absence':
					rec.write({'subject_status':'substitutional'})
			if rec.marksheet_line_id.student_id.id in rec.marksheet_line_id.marksheet_reg_id.exam_id.deprived_student_ids.mapped('student_id').ids:
				rec.write({'subject_status':'deprived'})


	
	@api.onchange('seeting_number')
	def _set_student_seeting_number(self):
		if self.student_id and self.seeting_number:
			self.student_id.seeting_number = self.seeting_number


	@api.depends('subject_total_degree','hour')
	def _get_subject_points(self):
		for rec in self:
			if rec.subject_total_degree:
				rec.subject_degree_point = rec.subject_total_degree / 20
				rec.subject_point = rec.subject_degree_point * rec.hour
			else:
				rec.subject_degree_point = 0
				rec.subject_point = 0


	@api.depends('attendees_degree','practical_degree','year_work_degree','final_exam_degree','exam_id.subject_id','exam_id.exam_date')
	def compute_final_degree(self):
		for rec in self:
			if rec.status == 'presence':
				if rec.exam_id.subject_id:
					year_work_prec = self.env['subject.degree.component'].search([('component_type','=','year_works'),('exam__id','=',rec.exam_id.id)],limit=1).percentage
					practical_perc = self.env['subject.degree.component'].search([('component_type','=','practical'),('exam__id','=',rec.exam_id.id)],limit=1).percentage
					attendees_perc = self.env['subject.degree.component'].search([('component_type','=','attendance'),('exam__id','=',rec.exam_id.id)],limit=1).percentage
					final_exam_perc = self.env['subject.degree.component'].search([('component_type','=','final_exam'),('exam__id','=',rec.exam_id.id)],limit=1).percentage
					rec.final_degree = rec.final_exam_degree*final_exam_perc/100+rec.year_work_degree*year_work_prec/100+rec.practical_degree*practical_perc/100+rec.attendees_degree*attendees_perc/100

				else:
					rec.final_degree = 0.0
			else:
				rec.final_degree = 0.0
				rec.final_exam_degree = 0.0

	@api.onchange('exam_id')
	def onchange_exam(self):
		self.student_id = False
		self.level_id = self.exam_id.level_id

	@api.onchange('status')
	def onchange_status(self):
		if self.status == 'absence':
			self.attendees_degree = 0.0
			self.practical_degree = 0.0
			self.year_work_degree = 0.0
			self.final_exam_degree = 0.0
			self.final_degree = 0.0

	@api.constrains('marks')
	def _check_marks(self):
		if self.marks < 0.0:
			raise ValidationError(_("Enter proper marks!"))
