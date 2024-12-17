import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StudentDegreesMigration(models.Model):
		_name = "student.degrees.migration"
		_description = "Student Degrees Migration"

		year_id = fields.Many2one(comodel_name='uni.year', string='Academic Year')
		batch_id = fields.Many2one(comodel_name='uni.faculty.department.batch')
		level_id = fields.Many2one(comodel_name='uni.faculty.level')
		semester_id = fields.Many2one(comodel_name='uni.faculty.semester', string='Term')
		program_id = fields.Many2one(comodel_name='uni.faculty.program')
		exam_type = fields.Many2one(comodel_name='uni.exam.types')
		exam = fields.Char(string='Exam Name')
		start_date = fields.Date('Start Date')
		end_date = fields.Date('End Date')
		student_ids = fields.Many2one(comodel_name='uni.student')
		code = fields.Char()
		subject_ids = fields.One2many(
		comodel_name="subjects.mapping",
		inverse_name="mapping_sub_id")
		active = fields.Boolean(default=True)
		state = fields.Selection(
		string="State",
		selection=[
				('draft', 'Draft'),
				('confirmed', 'Confirmed'),
				('done', 'Done'),
				],
			default='draft',
		)

		# @api.onchange('batch_id')
		# def onchange_batch(self):
		# 	self.subject_ids.unlink()
		# 	curriculum_line_id = self.env['uni.faculty.curriculum.line']
		# 	curriculum_id = self.env['uni.faculty.curriculum'].search([('program_id','=',self.program_id.id),('batch_id','=',self.batch_id.id)],limit=1)
			
		# 	if curriculum_id:
		# 		curriculum_line_id = self.env['uni.faculty.curriculum.line'].search([('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('curriculum_id','=',curriculum_id.id)])

		# 	for line in curriculum_line_id:
		# 		self.env['subjects.mapping'].create({
		# 			'subject_id':line.subject_id.id,
		# 			'mapping_sub_id':self.id,
		# 			})

		def create_subject_line(self):
			self.subject_ids.unlink()
			sublect_line = self.env['subjects.mapping'].create([
				{'mapping_sub':'sub1','mapping_sub_id':self.id},
				{'mapping_sub':'sub2', 'mapping_sub_id':self.id},
				{'mapping_sub':'sub3', 'mapping_sub_id':self.id},
				{'mapping_sub':'sub4', 'mapping_sub_id':self.id},
				{'mapping_sub':'sub5', 'mapping_sub_id':self.id},
				{'mapping_sub':'sub6', 'mapping_sub_id':self.id},
				{'mapping_sub':'sub7', 'mapping_sub_id':self.id},
				{'mapping_sub':'sub8', 'mapping_sub_id':self.id},
				{'mapping_sub':'sub9', 'mapping_sub_id':self.id},
				{'mapping_sub':'sub10', 'mapping_sub_id':self.id},
				])
	
		def to_confirmed(self):
			subjects = []
			for rec in self.subject_ids:
				if rec.mapping_sub:
					subjects.append(rec.subject_id.id)
			for line in self.env['student.degrees'].search([]):
				line.code = line.code.strip()
			subject_degrees_ids = self.env['student.degrees'].search([('code','=',self.code.strip())])
			students = []
			student_ids = []
			for rec in subject_degrees_ids:
				if rec.student_id.state == 'student' and rec.student_id.registration_status == 'registered':
					student_id = self.env['uni.student.exam'].search([('student_id','=',rec.student_id.id)],limit=1)
					if not student_id:
						student_exam_id = self.env['uni.student.exam'].create({
							'student_id':rec.student_id.id,
							})
					else:
						if self.exam_type.exam_category == 'first_round' and not self.exam_type.is_substitutionals:
							student_id.is_deprived = False
							student_id.exam_reason = False
							# student_id.supplement_subjects = [(6, 0, [])]
							# student_id.fulfillment_subjects = [(6, 0, [])]
							# student_id.substitutional_subjects = [(6, 0, [])]
							# student_id.repeat_subjects = [(6, 0, [])]
						student_exam_id = student_id
					students.append(student_exam_id.id)
					student_ids.append(rec.student_id)

			exam_record_id = self.env['uni.exam.record'].create({
				'name':self.exam,
				'code':self.code,
				'exam_type':self.exam_type.id,
				'start_date':self.start_date,
				'end_date':self.end_date,
				'academic_year_id':self.year_id.id,
				'program_id':self.program_id.id,
				'batch_id':self.batch_id.id,
				'level_id':self.level_id.id,
				'semester_id':self.semester_id.id,
				'subject_ids':[(6,0,subjects)],
				'student_ids':[(6,0,students)],
				})
			deprived_std_ids = exam_record_id.get_deprived_student()
			exceptional_std_ids = exam_record_id.get_exceptional_student()
			exam_record_id.write({
				'deprived_student_ids': [(6,0,deprived_std_ids)],
				'exceptional_student_ids':[(6,0,exceptional_std_ids)],
				})
			exam_record_id.check_end_level()
			exam_record_id._check_exam_category()
			if not exam_record_id.student_ids:
				raise ValidationError(_('You must get students firstly !!!!!'))
			exam_record_id.get_deprived_attendance()
			#exam_record_id.act_submit()
			self.create_exams(exam_record_id,student_ids,subjects)
			self.write({'state': 'confirmed'})


		def create_exams(self,exam_record_id,student_ids,subjects):
			time_table = self.env['generate.time.table'].search([('academic_year_id','=',self.year_id.id),
				('program_id','=',self.program_id.id),('level_id','=',self.level_id.id),
				('semester_id','=',self.semester_id.id),('batch_id','=',self.batch_id.id),
			] ,limit=1)
			attendees_line = exam_record_id.get_students(student_ids)

			for subject in subjects:
				subject = self.env['uni.faculty.subject'].browse(subject)
				exam = self.env['exam.exam'].create({
					'name': exam_record_id.name +' - '+ subject.name +' - '+ exam_record_id.program_id.name,
					'record_id':exam_record_id.id,
					'state':'draft',
					'subject_id':subject.id,
					'teacher_id': self.env['gen.time.table.line'].search([('gen_time_table','=',time_table.id),('subject_id','=',subject.id)]).teacher_id.id or False,
					'attendees_line':attendees_line,
				})
				for line in exam.attendees_line:
					line.compute_final_degree()
					line._compute_status()
				self.env['exam.template'].create({
					'exam_template_type': 'primary',
					'exam_id': exam.id,
				})
				self.env['exam.template'].create({
					'exam_template_type': 'substitutional',
					'exam_id': exam.id,
				})
				self.env['exam.template'].create({
					'exam_template_type': 'supplement',
					'exam_id': exam.id,
				})
				exam_record_id._get_exam_component(subject,exam)

			self.exam_degrees(exam_record_id)
			exam_record_id.write({'state': 'confirmed'})



		def exam_degrees(self,exam_record_id):
			exam_ids = self.env['exam.exam'].search([('record_id','=',exam_record_id.id)])
			for exam in exam_ids:
				subject_mapping_id = self.env['subjects.mapping'].search([('subject_id','=',exam.subject_id.id),('mapping_sub_id','=',self.id)],limit=1)
				for line in exam.attendees_line:
					student_degrees_id = self.env['student.degrees'].search([('student_id','=',line.student_id.id),('code','=',self.code)],limit=1)

					subject = 0
					if subject_mapping_id.mapping_sub == 'sub1':
						subject = student_degrees_id.sub1
					elif subject_mapping_id.mapping_sub == 'sub2':
						subject = student_degrees_id.sub2
					elif subject_mapping_id.mapping_sub == 'sub3':
						subject = student_degrees_id.sub3
					elif subject_mapping_id.mapping_sub == 'sub4':
						subject = student_degrees_id.sub4
					elif subject_mapping_id.mapping_sub == 'sub5':
						subject = student_degrees_id.sub5
					elif subject_mapping_id.mapping_sub == 'sub6':
						subject = student_degrees_id.sub6
					elif subject_mapping_id.mapping_sub == 'sub7':
						subject = student_degrees_id.sub7
					elif subject_mapping_id.mapping_sub == 'sub8':
						subject = student_degrees_id.sub8
					elif subject_mapping_id.mapping_sub == 'sub9':
						subject = student_degrees_id.sub9
					elif subject_mapping_id.mapping_sub == 'sub10':
						subject = student_degrees_id.sub10

					line.final_exam_degree =  subject
				# exam.act_schedule()
				# exam.act_done()

		def to_done(self):
			self.write({'state': 'done'})

		def to_draft(self):
			self.write({'state': 'draft'})


class SubjectsMapping(models.Model):
		_name = "subjects.mapping"
		_description = "Subjects Mapping"

		mapping_sub_id = fields.Many2one('student.degrees.migration')

		mapping_sub  = fields.Selection(
		string='Subject',
		selection=[
			('sub1', 'Subject(1)'),
			('sub2', 'Subject(2)'),
			('sub3', 'Subject(3)'),
			('sub4', 'Subject(4)'),
			('sub5', 'Subject(5)'),
			('sub6', 'Subject(6)'),
			('sub7', 'Subject(7)'),
			('sub8', 'Subject(8)'),
			('sub9', 'Subject(9)'),
			('sub10', 'Subject(10)')
			]
		)
		subject_id = fields.Many2one('uni.faculty.subject')

		subject_id_domain = fields.Char(
			compute="_compute_subject_id_domain",
			readonly=True,
			store=False,
			)

		semester_id = fields.Many2one("uni.faculty.semester", related='mapping_sub_id.semester_id')
		level_id = fields.Many2one("uni.faculty.level", related='mapping_sub_id.level_id')
		batch_id = fields.Many2one('uni.faculty.department.batch', related='mapping_sub_id.batch_id')
	

		@api.depends('batch_id','level_id','semester_id')
		def _compute_subject_id_domain(self):
			for rec in self:
				curriculum_id = self.env['uni.faculty.curriculum'].search([('program_id','=',rec.batch_id.program_id.id),('batch_id','=',rec.batch_id.id)],limit=1)
				if curriculum_id:
					curriculum_subjects_line_id = self.env['curriculum.subjects.line'].search([('level_id','=',rec.level_id.id),('semester_id','=',rec.semester_id.id),('program_id','=',rec.batch_id.program_id.id),('curriculum_id','=',curriculum_id.id)],limit=1)
				else:
					curriculum_subjects_line_id = self.env['curriculum.subjects.line'].search([('level_id','=',rec.level_id.id),('semester_id','=',rec.semester_id.id),('program_id','=',rec.batch_id.program_id.id)],limit=1)

				
				subjects = curriculum_subjects_line_id.subject_ids.ids

				rec.subject_id_domain = json.dumps(
				   [('id', 'in', subjects)]
				)
		