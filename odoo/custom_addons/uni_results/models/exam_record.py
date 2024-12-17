# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ExamRecord(models.Model):
	_name = "uni.exam.record"
	_inherit = ["mail.thread"]
	_description = "Exam Record"

	name = fields.Char(
		'Name', size=256, required=True, tracking=True)
	academic_year_id = fields.Many2one(
		'uni.year', 'Academic Year', required=True, tracking=True)
	program_id = fields.Many2one(
		'uni.faculty.program', 'Program', required=True, tracking=True)
	batch_id = fields.Many2one(
		'uni.faculty.department.batch', 'Batch', required=True, tracking=True)
	level_id = fields.Many2one(
		'uni.faculty.level', 'Level', required=True, tracking=True)
	semester_id = fields.Many2one(
		'uni.faculty.semester', "Term", required=True, tracking=True)
	code = fields.Char(
		'Code', size=16,
		required=True, tracking=True)
	start_date = fields.Date(
		'Start Date', tracking=True)
	end_date = fields.Date(
		'End Date', tracking=True)
	subject_ids = fields.Many2many(
		'uni.faculty.subject', string='Subjects', required=True)
	student_ids = fields.Many2many(
		'uni.student.exam', string='Students',copy=False)
	students = fields.Many2many('uni.student')
	deprived_student_ids = fields.Many2many(
		'uni.student.exam','exam_rel_deprived_student', string='Deprived Students',copy=False)
	exceptional_student_ids = fields.Many2many(
		'uni.student.exam','exam_rel_exceptional_student', string='Exceptional Students',copy=False)
	exam_type = fields.Many2one(
		'uni.exam.types', string='Exam Type',
		required=True, tracking=True)
	exam_category = fields.Selection(related="exam_type.exam_category")
	is_substitutionals = fields.Boolean(related="exam_type.is_substitutionals")
	is_supplement = fields.Boolean(compute="_check_exam_category")
	main_exam = fields.Many2one('uni.exam.record')
	substitutionals_exam = fields.Many2one('uni.exam.record')
	exam_ids = fields.One2many('exam.exam','record_id')

	end_level = fields.Boolean('End of Academic Level ?')

	state = fields.Selection([
		('draft', 'Draft'),
		('submit', 'Submited'),
		('confirmed', 'Confirmed'),
		('schedule', 'Scheduled'),
		('run', 'Run'),
		('done', 'Done')
	], 'State', default='draft', tracking=True)
	active = fields.Boolean(default=True)
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	

	@api.onchange('main_exam')
	def _get_main_exam_data(self):
		if self.main_exam:
			self.academic_year_id = self.main_exam.academic_year_id
			self.program_id = self.main_exam.program_id
			self.level_id = self.main_exam.level_id
			self.semester_id = self.main_exam.semester_id
			self.batch_id = self.main_exam.batch_id
			self.subject_ids = self.main_exam.subject_ids

	@api.onchange('is_substitutionals','is_supplement')
	def onchange_types(self):
		domain={}
		if self.is_substitutionals or self.is_supplement:
			domain = {
				'domain':{
					'main_exam':[('state','=','done'),('exam_category','=','first_round'),('is_supplement','!=',True),
					('is_substitutionals','!=',True)],
					'substitutionals_exam':[('state','=','done'),('exam_category','=','first_round'),
					('is_substitutionals','=',True)]}}

		return domain

	@api.depends('exam_category')
	def _check_exam_category(self):
		for rec in self:
			rec.is_supplement = False
			if rec.exam_category:
				if rec.exam_category == 'second_round':
					rec.is_supplement = True

	@api.onchange('semester_id')
	def check_end_level(self):
		if self.semester_id:
			if self.semester_id.order == '1':
				self.end_level = False
			elif self.semester_id.order == '2':
				self.end_level = True

			subjects = self.env['uni.faculty.curriculum.line'].search([
			('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),
			('curriculum_id','=',self.batch_id.curriculum_id.id)])
			subjects = subjects.mapped('subject_id')
			self.write({
				'subject_ids': [(6,0,subjects.ids)]
			})

	@api.onchange('student_ids')
	def _get_student_subject_attend(self):
		ids = []
		if self.student_ids:
			print('\n\n student_ids',self.student_ids)
			for student in self.student_ids:
				ids.append(student.student_id.id)

			self.write({'students':[(6,0,ids)]})

	@api.constrains('start_date', 'end_date')
	def _check_date_time(self):
		if self.start_date > self.end_date:
			raise ValidationError(
				_('End Date cannot be set before Start Date.'))

	@api.onchange('program_id')
	def onchange_program(self):
		domain={}
		if self.program_id:
			domain = {
					'domain':{
						'batch_id':[('program_id','=',self.program_id.id)],
						'student_ids':[('student_id.program_id','=',self.program_id.id)],
						'deprived_student_ids':[('student_id.program_id','=',self.program_id.id)],
						'exceptional_student_ids':['student_id.program_id','=',self.program_id.id]}}
		return domain

	@api.onchange('level_id')
	def onchange_level(self):
		domain={}
		if self.level_id:
			domain = {
				'domain':{
					'batch_id':[('level_id','=',self.level_id.id)],}}

			if self.program_id:
				domain = {
					'domain':{
						'batch_id':[('level_id','=',self.level_id.id),('program_id','=',self.program_id.id)],}}

		return domain

	@api.onchange('batch_id')
	def onchange_batch(self):
		if not self.semester_id:
			self.semester_id = self.batch_id.semester_id
		self.academic_year_id = self.batch_id.academic_year_id
		subjects = self.env['uni.faculty.curriculum.line'].search([
			('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),
			('curriculum_id','=',self.batch_id.curriculum_id.id)])
		subjects = subjects.mapped('subject_id')
		self.write({
			'subject_ids': [(6,0,subjects.ids)]
			})
		self.get_exam_dates()

	@api.onchange('exam_type')
	def get_exam_dates(self):
		calender_id = self.env['uni.faculty.calendar']
		self.start_date = False
		self.end_date = False
		level_id = self.batch_id.level_id 
		semester_id = self.batch_id.semester_id
		activity_id = self.env['uni.faculty.calendar.activities.line']
		calender_ids = self.env['uni.faculty.calendar'].search([('academic_year_id','=',self.academic_year_id.id),('state','=','approved')])
		if calender_ids:
			batch_calender_id = calender_ids.filtered(lambda l: self.batch_id.id in l.batch_ids.ids)
			if batch_calender_id:
				calender_id = batch_calender_id
			else:
				level_program_calender_id = calender_ids.filtered(lambda l: level_id.id in l.level_ids.ids and self.program_id in l.program_ids.ids)
				if level_program_calender_id:
					calender_id = level_program_calender_id
				else:
					level_calender_id = calender_ids.filtered(lambda l: level_id.id in l.level_ids.ids and not l.batch_ids and not l.program_ids)
					if level_calender_id:
						calender_id = level_calender_id
					else:
						program_calender_id = calender_ids.filtered(lambda l: self.program_id.id in l.program_ids.ids and not l.batch_ids and not l.level_ids)
						if program_calender_id:
							calender_id = program_calender_id
						else:
							year_calender_id = calender_ids.filtered(lambda l: not l.program_ids.ids and not l.batch_ids and not l.level_ids)
							calender_id = year_calender_id

			for activity in calender_id.calendar_activities_ids:
				if self.exam_type.exam_category == 'first_round'and not self.exam_type.is_substitutionals:
					if ((semester_id.order == '1') & (activity.name.activity_type == 'first_sem_exam')):
						activity_id = activity
						break
					elif ((semester_id.order == '2') & (activity.name.activity_type == 'sec_sem_exam')):
						activity_id = activity
						break
				elif self.exam_type.exam_category == 'first_round'and self.exam_type.is_substitutionals:
					if ((semester_id.order == '1') & (activity.name.activity_type == 'first_sem_sub_exam')):
						activity_id = activity
						break
					elif ((semester_id.order == '2') & (activity.name.activity_type == 'sec_sem_sub_exam')):
						activity_id = activity
						break
				elif self.exam_type.exam_category == 'second_round':
					if ((semester_id.order == '1') & (activity.name.activity_type == 'first_sem_supp_exam')):
						activity_id = activity
						break
					elif ((semester_id.order == '2') & (activity.name.activity_type == 'sec_sem_supp_exam')):
						activity_id = activity
						break

			self.start_date = activity_id.start_date
			self.end_date = activity_id.end_date



	def act_draft(self):
		self.student_ids = False
		self.deprived_student_ids = False
		self.exceptional_student_ids = False
		self.exam_ids.unlink()
		self.state = 'draft'

	def get_deprived_student(self):
		################# Deprived Students ###############
		deprived_student_ids = self.env['uni.student'].search([('program_id','=',self.program_id.id),
			('year_id','=',self.academic_year_id.id),('level_id','=',self.level_id.id),
			('semester_id','=',self.semester_id.id),('batch_id','=',self.batch_id.id),
			('registration_status','=','not_registered'),('academic_status','!=','dismiss'),
			('state','=','student')])
		deprived_student_ids = [student.id for student in deprived_student_ids]
		deprived_std_ids = []
		deprived_std = self.env['uni.student.exam']
		for student in deprived_student_ids:
			deprived_std = self.env['uni.student.exam'].search([('student_id','=',student)])
			if deprived_std:
				deprived_std.is_deprived = True
				deprived_std.exam_reason = False
				deprived_std.deprived_reason = 'Not Registered'
				deprived_std_ids.append(deprived_std.id)
			else:
				deprived_std = self.env['uni.student.exam'].create({
					'student_id':student,
					'seeting_number':0.0,
					'is_deprived': True,
					'deprived_reason':'Not Registered'
					})
				deprived_std_ids.append(deprived_std.id)

			if deprived_std.student_id.external:
				deprived_std.write({'exam_reason':'external'})
		return deprived_std_ids

	def get_exceptional_student(self):
		exceptional_ids = self.env['uni.student'].search([('program_id','=',self.program_id.id),
			('year_id','=',self.academic_year_id.id),('level_id','=',self.level_id.id),
			('semester_id','=',self.semester_id.id),('batch_id','=',self.batch_id.id),
			('registration_status','=','registered'),('state','in',['frozen','resigned','dismissed']),
		])
		print('-------------exceptional_ids ',exceptional_ids)
		exceptional_ids = [student.id for student in exceptional_ids]
		exceptional_std_ids = []
		exceptional_std = self.env['uni.student.exam']
		for student in exceptional_ids:
			exceptional_std = self.env['uni.student.exam'].search([('student_id','=',student)])
			if exceptional_std:
				exceptional_std.reason = False
				exceptional_std_ids.append(exceptional_std.id)
			else:
				exceptional_std = self.env['uni.student.exam'].create({
					'student_id':student,
					'seeting_number':0.0,
					})
				exceptional_std_ids.append(exceptional_std.id)

			if exceptional_std.student_id.state == 'frozen':
				exceptional_std.reason = 'frozen'

			if exceptional_std.student_id.state == 'resigned':
				exceptional_std.reason = 'resigned'

			if exceptional_std.student_id.state == 'dismissed':
				exceptional_std.reason = 'dismiss'
		return exceptional_std_ids

	def get_deprived_attendance(self):
		if self.company_id.attendance_perc:
			attend_percentage = self.company_id.attendance_perc
			time_table = self.env['generate.time.table'].search([
				('batch_id','=',self.batch_id.id),('program_id','=',self.program_id.id),
				('academic_year_id','=',self.academic_year_id.id),
				],limit=1)
			if time_table:
				deprived_std_ids = []
				deprived_dict = {}
				for subject in self.subject_ids:
					sessions = self.env['op.session'].search([('generation_id','=',time_table.id),('subject_id','=',subject.id)])
					subject_sessions = len(sessions)
					if sessions:
						for std in self.student_ids:
							if std.id not in self.exceptional_student_ids.ids and std.id not in self.deprived_student_ids.ids:
								counter = 0.0
								for session in sessions:
									for attendee in session.session_attendees_ids:
										if std.student_id.id == attendee.student_id.id:
											if attendee.status in ('presence','justified_absence'):
												counter += 1

									std_percentage = (counter / subject_sessions) * 100
									if std.student_id.id not in deprived_dict:
										deprived_dict[std.student_id.id] = [std_percentage]
									else:
										deprived_dict[std.student_id.id].append(std_percentage)
				
				for student in deprived_dict:
					subjects_no = len(deprived_dict[student])
					count = 0.0
					for val in deprived_dict[student]:
						if val < attend_percentage:
							count += 1
						if count == subjects_no:
							student_exam = self.env['uni.student.exam'].search([('student_id','=',student)])
							student_exam.deprived_reason = 'Low Attendance In All Subjects'

							self.write({
								'deprived_student_ids':[(4,student_exam.id)]
								})

							students = []
							for std in self.student_ids:
								if std.student_id.id not in self.deprived_student_ids.mapped('student_id').ids:
									students.append(std.id)
							self.write({
								'student_ids':[(6,0,students)]
								})		

	def _get_exam_students(self):
		################# Students ######################
		student_ids = self.env['uni.student'].search([('program_id','=',self.program_id.id),
			('year_id','=',self.academic_year_id.id),('level_id','=',self.level_id.id),
			('semester_id','=',self.semester_id.id),('batch_id','=',self.batch_id.id),
			('registration_status','=','registered'),('state','=','student'),
			('academic_status','not in',['substitutional_supplement','dismiss'])])
		students = [student.id for student in student_ids]
		std_ids = []
		std = self.env['uni.student.exam']
		for student in students:
			std = self.env['uni.student.exam'].search([('student_id','=',student)])
			if std:
				std.is_deprived = False
				std.exam_reason = False
				# std.supplement_subjects = [(6, 0, [])]
				# std.fulfillment_subjects = [(6, 0, [])]
				# std.substitutional_subjects = [(6, 0, [])]
				# std.repeat_subjects = [(6, 0, [])]
			else:
				std = self.env['uni.student.exam'].create({
					'student_id':student,
					'seeting_number':0.0,
					'is_deprived': False,
					})
			
			if std.id not in self.deprived_student_ids.ids:
				std_ids.append(std.id)

			if std.student_id.external:
				std.write({'exam_reason':'external'})
			if std.student_id.academic_status == 'repeat':
				std.write({'exam_reason':'repeat'})
			if std.student_id.academic_status == 'repeat_subjects':
				std.write({'exam_reason':'repeat_subjects'})
			
		############### get students has fulfillment subjects ############
		fulfillment_records = self.env['uni.admission.fulfillment.subject'].search([
			('academic_year_id','=',self.academic_year_id.id),('batch_id','=',self.batch_id.id),
			('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),
			('subject_id','in',self.subject_ids.ids),('admission_id.program_id','=',self.program_id.id),
			('admission_id.state','=','registered')])
		fulfillment_students = [record.student_id.id for record in fulfillment_records]

		for student in fulfillment_students:
			std = self.env['uni.student.exam'].search([('student_id','=',student)])
			fulfillment_subj = self.env['uni.admission.fulfillment.subject'].search([('academic_year_id','=',self.academic_year_id.id),('batch_id','=',self.batch_id.id),('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('subject_id','in',self.subject_ids.ids),('admission_id.program_id','=',self.program_id.id),('admission_id.state','=','registered')]).subject_id
			if std:
				std.is_deprived = False
				std.exam_reason = 'fulfilment'
				std.fulfillment_subjects = fulfillment_subj
			else:
				std = self.env['uni.student.exam'].create({
					'student_id':student,
					'seeting_number':0.0,
					'is_deprived': False,
					'exam_reason':'fulfilment',
					'fulfillment_subjects':[(6,0,fulfillment_subj.id)]
					})

			if std.id not in self.deprived_student_ids.ids:
				std_ids.append(std.id)
		return std_ids

	def act_get_students(self):
		std_ids = []
		if self.exam_category == 'first_round' and not self.is_substitutionals:

			exceptional_std_ids = self.get_exceptional_student()
			self.write({
				'exceptional_student_ids':[(6,0,exceptional_std_ids)]
				})


			deprived_std_ids = self.get_deprived_student()
			self.write({
				'deprived_student_ids': [(6,0,deprived_std_ids)],
				})

			
			std_ids = self._get_exam_students()
			# self.write({
			# 	'student_ids':[(6,0,std_ids)],
			# 	})

		################# substitutionals get students ##############
		elif self.exam_category == 'first_round' and self.is_substitutionals:
			ids = []
			for exam in self.main_exam.exam_ids:
				for attendee in exam.attendees_line:
					if attendee.status == 'justified_absence':
						ids.append(attendee.student_id.id)
						std_exam = self.env['uni.student.exam'].search([('student_id','=',attendee.student_id.id)])
						std_exam.write({'substitutional_subjects':[(4,exam.subject_id.id)]})

			std_ids = self.env['uni.student.exam'].search([('student_id','in',ids)]).ids
			# self.write({
			# 	'student_ids':[(6,0,std_ids)],
			# })
			
		################# supplements get students ##############
		elif self.exam_category == 'second_round':
			ids = []
			for exam in self.main_exam.exam_ids:
				for attendee in exam.attendees_line:
					if attendee.subject_status == 'fail':
						ids.append(attendee.student_id.id)
						std_exam = self.env['uni.student.exam'].search([('student_id','=',attendee.student_id.id)])
						std_exam.write({'supplement_subjects':[(4,exam.subject_id.id)]})

			for exam in self.substitutionals_exam.exam_ids:
				for attendee in exam.attendees_line:
					if attendee.subject_status in ['fail','substitutional']:
						ids.append(attendee.student_id.id)
						std_exam = self.env['uni.student.exam'].search([('student_id','=',attendee.student_id.id)])
						std_exam.write({'supplement_subjects':[(4,exam.subject_id.id)]})

			std_ids = self.env['uni.student.exam'].search([('student_id','in',ids)]).ids
			# self.write({
			# 	'student_ids':[(6,0,std_ids)],
			# })
		if not std_ids :
			raise ValidationError(_('There is no student'))

		else:
			self.write({
					'student_ids':[(6,0,std_ids)],
					})

	def act_submit(self):
		if not self.student_ids:
			raise ValidationError(_('You must get students firstly !!!!!'))
		self.get_deprived_attendance()
		self.act_confirm()
		self.state = 'confirmed'

	def act_confirm(self):
		################### get teacher #############
		time_table = self.env['generate.time.table'].search([('academic_year_id','=',self.academic_year_id.id),
			('program_id','=',self.program_id.id),('level_id','=',self.level_id.id),
			('semester_id','=',self.semester_id.id),('batch_id','=',self.batch_id.id),
			],limit=1)
		
		if self.exam_category == 'first_round' and not self.is_substitutionals:
			for subject in self.subject_ids:
				attendees_line =[]
				student_ids = []
				curriculum_line_id = self.env['uni.faculty.curriculum.line'].search([('curriculum_id','=',self.batch_id.curriculum_id.id),('subject_id','=',subject.id),('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id)],limit=1)
				if curriculum_line_id.specialization_id:
					for std in self.student_ids:
						if std.student_id.specialization_id.id == curriculum_line_id.specialization_id.id:
							student_ids.append(std.student_id)
				else:
					for std in self.student_ids:
						student_ids.append(std.student_id)

				########### student fulfillment subject in exam ############## 
				new_student_ids = []
				for std in student_ids:
					student = self.env['uni.student.exam'].search([('student_id','=',std.id)])
					if student.fulfillment_subjects:
						if subject.id not in student.fulfillment_subjects.ids:
							pass
						else:
							new_student_ids.append(std)
					else:
						new_student_ids.append(std)
				if not new_student_ids:
					new_student_ids = student_ids

				attendees_line = self.get_students(new_student_ids)
				exam = self._create_exam(subject,time_table,attendees_line)
				
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

				self._get_exam_component(subject,exam)

		elif self.exam_category == 'first_round' and self.is_substitutionals:
			subjects = []
			subjects_dict = {}
			for student in self.student_ids:
				for subj in student.substitutional_subjects:
					if subj in subjects:
						pass
					else:
						subjects.append(subj)

					if subj not in subjects_dict:
						subjects_dict[subj] = [student.student_id.id]
					else:
						subjects_dict[subj].append(student.student_id.id)

			############# create exams ##################		
			for subject ,students in subjects_dict.items():
				student_ids = self.env['uni.student'].search([('id','in',students)])
				attendees_line = self.get_students(student_ids)

				exam = self._create_exam(subject,time_table,attendees_line)
				self._get_exam_component(subject,exam)

		elif self.exam_category == 'second_round':
			subjects = []
			subjects_dict = {}
			for student in self.student_ids:
				for subj in student.supplement_subjects:
					if subj in subjects:
						pass
					else:
						subjects.append(subj)

					if subj not in subjects_dict:
						subjects_dict[subj] = [student.student_id.id]
					else:
						subjects_dict[subj].append(student.student_id.id)

			############# create exams ##################		
			for subject ,students in subjects_dict.items():
				student_ids = self.env['uni.student'].search([('id','in',students)])
				attendees_line = self.get_students(student_ids)

				exam = self._create_exam(subject,time_table,attendees_line)
				self._get_exam_component(subject,exam)


		self.state = 'confirmed'

	def _create_exam(self,subject,time_table,attendees_line):
		new_attendees = []
		if self.exam_category == 'first_round' and not self.is_substitutionals:
			for attend in attendees_line:
				student_exam = self.env['uni.student.exam'].search([('student_id','=',attend[2]['student_id'])])
				if student_exam.repeat_subjects:
					if subject.id in student_exam.repeat_subjects.ids:
						new_attendees.append(attend)
				else:
					new_attendees.append(attend)
		print('------------ new_attendees',new_attendees,attendees_line)
					
		exam = self.env['exam.exam'].create({
			'name': self.name +' - '+ subject.name +' - '+ self.program_id.name,
			'record_id':self.id,
			'state':'draft',
			'subject_id':subject.id,
			'teacher_id': self.env['gen.time.table.line'].search([('gen_time_table','=',time_table.id),('subject_id','=',subject.id)],limit=1).teacher_id.id or False,
			'attendees_line':new_attendees if new_attendees else attendees_line,
		})
		exam._get_deprived_stds()
		return exam

	def _get_exam_component(self,subject,exam):
		curriculum_line = self.env['uni.faculty.curriculum.line'].search([('curriculum_id','=',self.batch_id.curriculum_id.id),('subject_id','=',subject.id),('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id)],limit=1)
		component = []
		if curriculum_line:
			if curriculum_line.full_degree > 0 and curriculum_line.success_degree > 0:
				exam.write({
					'full_degree':curriculum_line.full_degree,
					'success_degree':curriculum_line.success_degree,
				})
			else:
				exam.write({
					'full_degree':100,
					'success_degree':50,
				})

			if curriculum_line.degree_component:
				for degree in curriculum_line.degree_component:
					component.append([0,0,{
						'name':degree.name.id,
						'component_type':degree.component_type,
						'percentage':degree.percentage,
						'exam__id': exam.id
					}])
			else:
				name = self.env['degree.component'].search([('component_type','=','final_exam')],limit=1)
				component.append([0,0,{
					'name':name.id if name else self.env['degree.component'].create({'name':'الإمتحان','component_type':'final_exam'}).id,
					'component_type':'final_exam',
					'percentage':100,
					'exam__id': exam.id
				}])
			exam.write({
				'degree_component':component,
			})
		else:
			exam.write({
				'full_degree':100,
				'success_degree':50,
			})
			name = self.env['degree.component'].search([('component_type','=','final_exam')],limit=1)
			component.append([0,0,{
				'name':name.id if name else self.env['degree.component'].create({'name':'الإمتحان','component_type':'final_exam'}).id,
				'component_type':'final_exam',
				'percentage':100,
				'exam__id': exam.id
			}])
			exam.write({
				'degree_component':component,
			})


	def get_students(self,student_ids):
		attendees_line = []
		for student in student_ids:
			if student.id in self.student_ids.mapped('student_id').ids:
				attendees_line.append(([0,0,{
					'student_id':student.id,
					'seeting_number':self.student_ids.search([('student_id','=',student.id)]).seeting_number,
					'university_id':student.university_id,
					}]))
		return attendees_line

	def act_schedule(self):
		for exam in self.exam_ids:
			if exam.state == 'draft':
				raise ValidationError(_('Please make sure all exams are scheduling!!'))
		self.state = 'schedule'

	def act_run(self):
		self.state = 'run'

	def act_done(self):
		self.state = 'done'

	def exam_tree_view(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Exams',
			'view_mode': 'tree,form',
			'res_model': 'exam.exam',
			'domain': [('record_id', '=', self.id)],
			'context': {'default_record_id': self.id},

		}

	def unlink(self):
		for exam in self.exam_ids:
			if exam.state != 'draft':
				raise ValidationError(
				_('There is an exam related to this exam record that is not in draft state.'))
			else:
				exam.unlink()
		res = super(ExamRecord,self).unlink()
		return res

class ExamStudents(models.Model):
	_name = 'uni.student.exam'

	student_id = fields.Many2one('uni.student')
	program_id = fields.Many2one(
		'uni.faculty.program',
		related='student_id.program_id'
	)
	university_id = fields.Char(
		string='University ID',
		related='student_id.university_id'
	)
	std_number = fields.Char(
		string='Student Number',
		related='student_id.std_number'
		)
	seeting_number = fields.Char()
	is_deprived = fields.Boolean(default=False)
	deprived_reason = fields.Char()
	exam_reason = fields.Selection(selection=[
		('repeat','Repeat'),('repeat_subjects','Repeat With Subjects'),
		('carry','Carry'),('external','External'),('frozen','Suspended'),
		('bridging','Bridging'),('fulfilment','Fulfilment'),
		('resigned','Resigned'),('dismiss','Dismissed'),
		('low_attendance','Low Attendance In All Subjects'),
		('not_registered','Not Registerd'),
	])
	reason = fields.Selection(selection=[
		('frozen','Suspended'),('resigned','Resigned'),('dismiss','Dismissed')
		])
	substitutional_subjects = fields.Many2many('uni.faculty.subject','substitutionals_rel_student')
	supplement_subjects = fields.Many2many('uni.faculty.subject','supplements_rel_student')
	fulfillment_subjects = fields.Many2many('uni.faculty.subject','fulfillments_rel_student')
	repeat_subjects = fields.Many2many('uni.faculty.subject','repeat_subject_rel_student')


	def move_frozen_student(self):		
		self.env.cr.execute('select uni_exam_record_id from exam_rel_exceptional_student where uni_student_exam_id = %s' % self.id)
		rec = self.env.cr.fetchall()
		rec = rec[0][0]
		self.env.cr.execute('insert into uni_exam_record_uni_student_exam_rel (uni_exam_record_id,uni_student_exam_id) VALUES(%s,%s)' % (rec,self.id))
		self.env.cr.execute('delete from exam_rel_exceptional_student where uni_student_exam_id = %s' % self.id)
		if self.student_id.state == 'frozen':
			self.exam_reason = 'frozen'
		if self.student_id.state == 'resigned':
			self.exam_reason = 'resigned'
		if self.student_id.state == 'dismissed':
			self.exam_reason = 'dismiss'

	def move_deprived_student(self):
		self.env.cr.execute('select uni_exam_record_id from exam_rel_deprived_student where uni_student_exam_id = %s' % self.id)
		rec = self.env.cr.fetchall()
		rec = rec[0][0]
		self.env.cr.execute('insert into uni_exam_record_uni_student_exam_rel (uni_exam_record_id,uni_student_exam_id) VALUES(%s,%s)' % (rec,self.id))
		self.env.cr.execute('delete from exam_rel_deprived_student where uni_student_exam_id = %s' % self.id)
		if self.deprived_reason == 'Low Attendance In All Subjects':
			self.exam_reason = 'low_attendance'
		elif self.deprived_reason == 'Not Registered':
			self.exam_reason = 'not_registered'
		exam_record_id = self.env['uni.exam.record'].browse(rec)
		if exam_record_id.state == 'confirmed':
			for exam in exam_record_id.exam_ids:
				exam.attendees_line = [(0,0,{'student_id':self.student_id.id,'seeting_number':self.seeting_number})]



	@api.onchange('seeting_number')
	def _set_student_seeting_number(self):
		if self.student_id and self.seeting_number:
			self.student_id.seeting_number = self.seeting_number