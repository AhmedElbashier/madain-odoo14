

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpMarksheetLine(models.Model):
	_name = "marksheet.line"
	_rec_name = "student_id"
	_description = "Marksheet Line"

	
	student_id = fields.Many2one('uni.student', 'Student', required=True)
	
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

	program_id = fields.Many2one(
		'uni.faculty.program',
		string='Program',
	)

	batch_id = fields.Many2one(
		'uni.faculty.department.batch',
		string='Batch',
	)
	marksheet_reg_id = fields.Many2one(
		'marksheet.register', 'Marksheet Register')
	end_level = fields.Boolean(related='marksheet_reg_id.end_level')
	attendees_line = fields.One2many(
		'exam.attendees', 'marksheet_line_id', 'Results')
	# substitutional_attendees_line = fields.One2many(
	# 	'exam.attendees', 'mark_line_id', 'Results')
	total_points = fields.Float("Total Points",
								 compute='_compute_total_points_hours',
								 )
	total_hours = fields.Float("Total Hours",
								 compute='_compute_total_points_hours',
								 )
	generated_date = fields.Date(
		'Generated Date', required=True,
		default=fields.Date.today(), tracking=True)
	result_id = fields.Many2one('uni.result.record')
	sgpa = fields.Float('SGPA1',compute="_calc_sgpa", store=True)
	sgpa2 = fields.Float('SGPA2',compute="_calc_sgpa", store=True)
	sgpa_grade_letter = fields.Char('Grade Letter', readonly=True)
	sgpa_grade = fields.Char('Grade', readonly=True)
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	gpa = fields.Float(compute='_calc_gpa', string="GPA", store=True)
	status = fields.Selection([
		('pass','Pass'),
		('substitutional','Substitutionals'),
        ('supplement','Supplements'),
        ('substitutional_supplement','Substitutionals & Supplements'),
        ('removal','Removal'),
        ('repeat','Repeat'),
        ('repeat_subjects','Repeat With Subjects'),
        ('dismiss','Dismiss'),
        ('dismissed_absence','Dismissed for Absence'),
		])
	academic_status = fields.Selection(
        string="Acadimic Status",
        selection=[
            ('fresh', 'Fresh'),
            ('success', 'Success'),
            ('repeat', 'Repeat'),
            ('repeat_subjects','Repeat With Subjects'),
            ('supplement' , 'Has Supplements'),
            ('substitutions', 'Has Substitutionals'),
            ('substitutional_supplement','Has Substitutionals & Supplements'),
            ('dismiss','Dismiss'),
        ],
        default='fresh',
    )

	@api.depends('end_level')
	def _calc_gpa(self):
		for rec in self:
			points = 0
			hours = 0
			if rec.marksheet_reg_id.exam_id.end_level:
				level = rec.marksheet_reg_id.exam_id.level_id
				lines = self.env['marksheet.line'].search([('level_id','=',level.id),('student_id','=',rec.student_id.id)])
				std_lines = {}
				for line in lines:
					points += line.total_points
					hours += line.total_hours
				rec.gpa = points/hours
			else:
				rec.gpa = 0
			rec.calculate_student_status()
			

	@api.depends('attendees_line.subject_point','attendees_line.hour','attendees_line.program_council_push','attendees_line.scientific_council_push')
	def _compute_total_points_hours(self):
		for rec in self:
			rec.total_points = 0
			rec.total_hours = 0
			if rec.attendees_line:
				for att in rec.attendees_line:
					if att.exam_id.record_id.exam_category == 'first_round' and not att.exam_id.record_id.is_substitutionals:
						
						if att.status != 'justified_absence':
							print('------------- if',rec.total_points)
							rec.total_points += att.subject_point
							rec.total_hours += att.hour
					else:
						print('------------ else')
						rec.total_points += att.subject_point
						rec.total_hours += att.hour
				print('------------ rec.total_points',rec.total_points,rec.total_hours)

	@api.onchange('student_id')
	def get_data(self):
		for rec in self:
			if rec.student_id:
				rec.year_id = rec.student_id.year_id
				rec.level_id = rec.student_id.level_id
				rec.semester_id = rec.student_id.semester_id
				rec.batch_id = rec.student_id.batch_id
				rec.program_id = rec.student_id.program_id  

	@api.depends('total_points','total_hours')
	def _calc_sgpa(self):
		for rec in self:
			rec.status = False
			sgpa = 0
			if rec.total_hours > 0:
				sgpa = rec.total_points / rec.total_hours
				if rec.marksheet_reg_id.end_level:
					rec.sgpa2 = sgpa
					marksheet_line_id = self.search([('student_id','=',rec.student_id.id),
						('marksheet_reg_id.exam_id.exam_type.exam_category','=','first_round'),
						('marksheet_reg_id.exam_id.exam_type.is_substitutionals','!=',True),
						('level_id','=',rec.level_id.id),('id','!=',rec._origin.id)],limit=1)
					if marksheet_line_id:
						rec.sgpa = marksheet_line_id.sgpa

					rec._calc_gpa()
				else:
					rec.sgpa = sgpa
					rec.sgpa2 = 0
			else:
				rec.sgpa = 0
				rec.sgpa2 = 0
			rec._compute_sgpa_grade()
			

			
	def calculate_student_status(self):
		for rec in self:
			if rec.marksheet_reg_id.exam_id.end_level:
				if rec.marksheet_reg_id.exam_id.exam_type.exam_category == 'first_round' and not rec.marksheet_reg_id.exam_id.exam_type.is_substitutionals:
					if rec.gpa >= 2.5:
						substitutional_exam_attendees_id = rec.attendees_line.search([
							('marksheet_line_id','=',rec.id),('subject_status','=','substitutional'),('status','=','justified_absence')])

						supplement_exam_attendees_id = rec.attendees_line.search([
							('marksheet_line_id','=',rec.id),('subject_status','=','fail'),('status','in',['presence','absence'])])

						if substitutional_exam_attendees_id and supplement_exam_attendees_id:
							rec.status = 'substitutional_supplement'
						elif supplement_exam_attendees_id and not substitutional_exam_attendees_id:
							rec.status = 'supplement'
						elif substitutional_exam_attendees_id and not supplement_exam_attendees_id:
							rec.status = 'substitutional'
						else:
							rec.status = 'pass'
					elif rec.gpa < 2.5:
						subjects_no = len(rec.attendees_line)
						counter = 0
						ids = []
						for line in rec.attendees_line:
							if line.subject_status not in ['pass','substitutional']:
								counter += 1
								ids.append(line.subject.id)
						if counter > 0:
							num = subjects_no/2
							if counter <= num:
								rec.status = 'repeat_subjects'
								student_exam = self.env['uni.student.exam'].search([('student_id','=',rec.student_id.id)])
								student_exam.write({
									'repeat_subjects':[(6,0,ids)]
									})
							else:
								rec.status = 'repeat'

								# if rec.student_id.study_year_no > rec.program_id.maximum_study_years:
								# 	rec.status = 'dismiss'
						else:
							rec.status = 'repeat'

							# if rec.student_id.study_year_no > rec.program_id.maximum_study_years:
							# 	rec.status = 'dismiss'

					elif rec.gpa == 0.0:
						rec.status = ''

				if rec.marksheet_reg_id.exam_id.exam_type.exam_category == 'first_round' and rec.marksheet_reg_id.exam_id.exam_type.is_substitutionals:
					if rec.gpa >= 2.5:
						status_exam_attendees_id = rec.attendees_line.search([
							('marksheet_line_id','=',rec.id),
							('status','=','justified_absence')])					
						subject_status_exam_attendees_id = rec.attendees_line.search([
							('marksheet_line_id','=',rec.id),
							('subject_status','in',['fail','absence'])])
						if subject_status_exam_attendees_id or status_exam_attendees_id:
							rec.status = 'supplement'
						else:
							rec.status = 'pass'
					elif rec.gpa < 2.5:
						subjects_no = len(rec.attendees_line)
						counter = 0
						ids = []
						for line in rec.attendees_line:
							if line.subject_status not in ['pass','substitutional']:
								counter += 1
								ids.append(line.subject.id)
						if counter > 0:
							num = subjects_no/2
							if counter <= num:
								rec.status = 'repeat_subjects'
								student_exam = self.env['uni.student.exam'].search([('student_id','=',rec.student_id.id)])
								student_exam.write({
									'repeat_subjects':[(6,0,ids)]
									})
							else:
								rec.status = 'repeat'

								# if rec.student_id.study_year_no > rec.program_id.maximum_study_years:
								# 	rec.status = 'dismiss'
						else:
							rec.status = 'repeat'

							# if rec.student_id.study_year_no > rec.program_id.maximum_study_years:
							# 	rec.status = 'dismiss'

					elif rec.gpa == 0.0:
						rec.status = ''
			else:
				rec.status = ''

	def _compute_sgpa_grade(self):
		for rec in self:
			rec.sgpa_grade_letter = ''
			rec.sgpa_grade = ''
			grade = self.env['grade.conf']
			if rec.marksheet_reg_id.end_level:
				if rec.level_id.level_grade:
					grade = rec.level_id.level_grade
				elif rec.program_id.curriculum_id.level_grade:
					grade = rec.program_id.curriculum_id.level_grade
				elif rec.company_id.level_grade:
					grade = rec.company_id.level_grade
				else:
					raise ValidationError(_('Sorry you must configr the grade configuration'))

				for categ in grade.category_ids:
					if rec.gpa >= categ.minimum_degree and rec.gpa <= categ.maximum_degree:
						rec.sgpa_grade_letter = categ.grade_letter
						rec.sgpa_grade = categ.grade
					
			else:
				if rec.semester_id.semester_grade:
					grade = rec.semester_id.semester_grade
				elif rec.program_id.curriculum_id.semester_grade:
					grade = rec.program_id.curriculum_id.semester_grade
				elif rec.company_id.semester_grade:
					grade = rec.company_id.semester_grade
				else:
					raise ValidationError(_('Sorry you must configr the grade configuration'))

				for categ in grade.category_ids:
					if rec.sgpa >= categ.minimum_degree and rec.sgpa <= categ.maximum_degree:
						rec.sgpa_grade_letter = categ.grade_letter
						rec.sgpa_grade = categ.grade
					
