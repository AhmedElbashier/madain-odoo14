# -*- coding: utf-8 -*-

import calendar
import datetime
import pytz
import time

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

PRACTICAL_SELECTION = [('practical','Practical')]
THEORETICAL_SELECTION = [('theoretical','Theoretical')]
PRACTICAL_THEORETICAL = [('practical','Practical'),('theoretical','Theoretical')]


class GenerateSession(models.Model):
	_name = "generate.time.table"
	_inherit = ["mail.thread"]
	_description = "Generate Sessions"
	_rec_name = "batch_id"

	course_id = fields.Char('Course')

	academic_year_id = fields.Many2one(
		'uni.year',
		string="Academic Year",
		required=True
	)
	level_id = fields.Many2one(
		string="Level",
		comodel_name="uni.faculty.level",
		required=True,
	)
	semester_id = fields.Many2one(
		string="Term",
		comodel_name="uni.faculty.semester",
		required=True,
	)
	term_semester_id = fields.Char(compute="compute_semeser",string='Semester', store=True)

	state = fields.Selection([
		('draft','Draft'),
		('approved','Approved'),
		('closed','Closed'),
		],default='draft')

	program_id = fields.Many2one(
		'uni.faculty.program', 'Program', required=True)
	batch_id = fields.Many2one('uni.faculty.department.batch', domain=[('program_id','=',program_id), ], string='Batch', required=True)
	
	session_count = fields.Integer(compute='_compute_seesions')
	
	time_table_lines = fields.One2many(
		'gen.time.table.line', 'gen_time_table', 'Time Table Lines')
	time_table_lines_1 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', 'Time Table Lines1',
		domain=[('day', '=', '2')])
	time_table_lines_2 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', 'Time Table Lines2',
		domain=[('day', '=', '3')])
	time_table_lines_3 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', 'Time Table Lines3',
		domain=[('day', '=', '4')])
	time_table_lines_4 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', 'Time Table Lines4',
		domain=[('day', '=', '5')])
	time_table_lines_5 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', 'Time Table Lines5',
		domain=[('day', '=', '6')])
	time_table_lines_6 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', 'Time Table Lines6',
		domain=[('day', '=', '0')])
	time_table_lines_7 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', 'Time Table Lines7',
		domain=[('day', '=', '1')])
	start_date = fields.Date(
		'Start Date', required=True)
	end_date = fields.Date('End Date', required=True)



	@api.depends('level_id','semester_id')
	def compute_semeser(self):
		for rec in self:
			if rec.semester_id.order == '2':
				rec.term_semester_id = int(rec.level_id.order)*int(rec.semester_id.order)
			elif rec.semester_id.order == '1':
				rec.term_semester_id = (int(rec.level_id.order)*2)-1

	@api.onchange('program_id')
	def onchange_program_id(self):
		domain = {}
		self.batch_id = False
		domain = {
			'domain':{
				'batch_id':[('program_id','=',self.program_id.id),('state','=','under_study')],
				
			}
		}
	   
		return domain

	@api.onchange('academic_year_id','semester_id','program_id','batch_id')
	def onchange_semester(self):
		calender_id = self.env['uni.faculty.calendar']
		self.start_date = False
		self.end_date = False
		self.level_id = self.batch_id.level_id.id 
		self.semester_id = self.batch_id.semester_id.id
		activity_id = self.env['uni.faculty.calendar.activities.line']
		calender_ids = self.env['uni.faculty.calendar'].search([('academic_year_id','=',self.academic_year_id.id),('state','=','approved')])
		if calender_ids:
			batch_calender_id = calender_ids.filtered(lambda l: self.batch_id.id in l.batch_ids.ids)
			if batch_calender_id:
				calender_id = batch_calender_id
			else:
				level_program_calender_id = calender_ids.filtered(lambda l: self.level_id.id in l.level_ids.ids and self.program_id in l.program_ids.ids)
				if level_program_calender_id:
					calender_id = level_program_calender_id
				else:
					level_calender_id = calender_ids.filtered(lambda l: self.level_id.id in l.level_ids.ids and not l.batch_ids and not l.program_ids)
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
				if ((self.semester_id.order == '1') & (activity.name.activity_type == 'first_sem')):
					activity_id = activity
					break
				elif ((self.semester_id.order == '2') & (activity.name.activity_type == 'second_sem')):
					activity_id = activity
					break

			self.start_date = activity_id.start_date
			self.end_date = activity_id.end_date


	def _compute_seesions(self):

		data = self.env['op.session'].read_group([('generation_id', 'in', self.ids)], ['generation_id'], 'generation_id')
		mapped_data = dict([(d['generation_id'][0], d['generation_id_count']) for d in data])
		for model in self:
			model.session_count = mapped_data.get(model.id, 0)

	@api.constrains('start_date', 'end_date')
	def check_dates(self):
		start_date = fields.Date.from_string(self.start_date)
		end_date = fields.Date.from_string(self.end_date)
		if start_date > end_date:
			raise ValidationError(_("End Date cannot be set before \
			Start Date."))

	def check_subject(self):
		curriculum_line_ids = self.env['uni.faculty.curriculum.line'].search([('curriculum_id','=',self.batch_id.curriculum_id.id),('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id)])
		print('----------- curriculum',curriculum_line_ids,self.batch_id.curriculum_id)
		for line in curriculum_line_ids:
			print('----------line',line.subject_id.name,line.subject_id.subject_type)
			if line.subject_type == 'theoretical':
				time_table_line_id = self.env['gen.time.table.line'].search([('gen_time_table','=',self.id),('subject_type','=','theoretical'),('subject_id','=',line.subject_id.id)])
				print('--------------- if',time_table_line_id)
				if not time_table_line_id:
					raise ValidationError(_("%s" %line.subject_id.name+"  does not have a theoretical lecture."))

			elif line.subject_type == 'practical':
				time_table_line_id = self.env['gen.time.table.line'].search([('gen_time_table','=',self.id),('subject_type','=','practical'),('subject_id','=',line.subject_id.id)])
				print('--------------- elif',time_table_line_id)
				if not time_table_line_id:
					raise ValidationError(_("%s" %line.subject_id.name+"  does not have a practical lecture."))

			else:
				theoretical_time_table_line_id = self.env['gen.time.table.line'].search([('gen_time_table','=',self.id),('subject_type','=','theoretical'),('subject_id','=',line.subject_id.id)])
				practical_time_table_line_id = self.env['gen.time.table.line'].search([('gen_time_table','=',self.id),('subject_type','=','practical'),('subject_id','=',line.subject_id.id)])
				print('--------------- else',theoretical_time_table_line_id,practical_time_table_line_id)

				if not theoretical_time_table_line_id:
					raise ValidationError(_("%s" %line.subject_id.name+"  does not have a theoretical lecture."))
				if not practical_time_table_line_id:
					raise ValidationError(_("%s" %line.subject_id.name+"  does not have a practical lecture."))


	def get_subject_dic(self):
		theoretical = {}
		practical = {}
		for line in self.time_table_lines:
			if line.subject_type == 'theoretical':
				if line.subject_id.id in theoretical.keys():
					theoretical[line.subject_id.id] = theoretical.get(line.subject_id.id)+1
				else:
					theoretical[line.subject_id.id] = 1
			else:
				if line.subject_id.id in practical.keys():
					practical[line.subject_id.id] = practical.get(line.subject_id.id)+1
				else:
					practical[line.subject_id.id] = 1

		return theoretical,practical

	def get_session_number(self,line,session_number,theoretical,practical):
		if line.subject_type == 'theoretical' and line.subject_id.id in theoretical.keys():
				session_number = theoretical.get(line.subject_id.id)
				theoretical[line.subject_id.id] = session_number+1
		else:
			if line.subject_id.id in practical.keys():
				session_number = practical.get(line.subject_id.id)
				practical[line.subject_id.id] = session_number+1

		return session_number


	def act_gen_time_table(self):
		self.check_subject()
		theoretical,practical = self.get_subject_dic()
		session_obj = self.env['op.session']
		for session in self:
			start_date = session.start_date
			end_date = session.end_date
			session_no = 0
			for n in range((end_date - start_date).days + 1):
				curr_date = start_date + datetime.timedelta(n)
				for line in session.time_table_lines:
					duration = line.hours
					if int(line.day) == curr_date.weekday():
						hour = line.timing_id.hour
						if line.timing_id.am_pm == 'pm' and int(hour) != 12:
							hour = int(hour) + 12
						per_time = '%s:%s:00' % (hour, line.timing_id.minute)
						final_date = datetime.datetime.strptime(
							curr_date.strftime('%Y-%m-%d ') +
							per_time, '%Y-%m-%d %H:%M:%S')
						local_tz = pytz.timezone(
							self.env.user.partner_id.tz or 'GMT')
						local_dt = local_tz.localize(final_date, is_dst=None)
						utc_dt = local_dt.astimezone(pytz.utc)
						utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
						curr_start_date = datetime.datetime.strptime(
							utc_dt, "%Y-%m-%d %H:%M:%S")
						curr_end_date = curr_start_date + datetime.timedelta(
							hours=duration)
						session_number = 0
						session_number = self.get_session_number(line,session_number,theoretical,practical)
						session_obj.create({
							'session_number':session_number,
							'faculty_id': line.faculty_id.id,
							'subject_id': line.subject_id.id,
							'program_id':line.program_id.id,
							'level_id':line.level_id.id,
							'semester_id':line.semester_id.id,
							'subject_type':line.subject_type,
							'subject_groups':line.subject_groups.id,
							'batch_id': session.batch_id.id,
							'timing_id': line.timing_id.id,
							'classroom_id': line.classroom_id.id,
							'start_datetime':
							curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
							'end_datetime':
							curr_end_date.strftime("%Y-%m-%d %H:%M:%S"),
							'type': calendar.day_name[int(line.day)],
							'generation_id':session.id,
							#'session_attendees_ids': attendees_line,
						})
			self.state = 'approved'
			return {'type': 'ir.actions.act_window_close'}

	def action_close(self):
		self.state = 'closed'

	def rest_draft(self):
		self.state = 'draft'

	def open_sessions(self):
		"""
			 Method To open session records related to active batch
		"""
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Sessions',
			'view_mode': 'kanban,tree,form',
			'res_model': 'op.session',
			'domain': [('generation_id', '=', self.id)],
		}


class GenerateSessionLine(models.Model):
	_name = 'gen.time.table.line'
	_description = 'Generate Time Table Lines'
	_rec_name = 'day'

	gen_time_table = fields.Many2one(
		'generate.time.table', 'Time Table', required=True)
	program_id = fields.Many2one('uni.faculty.program', related='gen_time_table.program_id')
	faculty_id = fields.Many2one('uni.faculty.program', related='gen_time_table.program_id', string='Program')
	semester_id = fields.Many2one("uni.faculty.semester", related='gen_time_table.semester_id')
	level_id = fields.Many2one("uni.faculty.level", related='gen_time_table.level_id')
	batch_id = fields.Many2one('uni.faculty.department.batch', related='gen_time_table.batch_id')
	academic_year_id = fields.Many2one('uni.year', related='gen_time_table.academic_year_id')
	subject_id = fields.Many2one('uni.faculty.subject', 'Subject', required=True)
	theoretical_subject = fields.Selection(selection=THEORETICAL_SELECTION)
	practical_subject = fields.Selection(selection=PRACTICAL_SELECTION)
	practical_theoretical_subject = fields.Selection(selection=PRACTICAL_THEORETICAL)
	subject_type = fields.Selection(string='Type', selection=PRACTICAL_SELECTION+THEORETICAL_SELECTION+PRACTICAL_THEORETICAL, store=True, readonly=False, required=True)
	teacher_id = fields.Many2one('hr.employee','Teacher', required=True)
	subject_groups = fields.Many2one('uni.student.groups',string="Group")
	timing_id = fields.Many2one('op.timing', 'Start Time ', required=True)
	end_time = fields.Float('End Time ',compute="_compute_end_time", store=True)
	hours = fields.Float(required=True)
	classroom_id = fields.Many2one('uni.faculty.classroom', 'Classroom', required=True)
	day = fields.Selection([
		('0', calendar.day_name[0]),
		('1', calendar.day_name[1]),
		('2', calendar.day_name[2]),
		('3', calendar.day_name[3]),
		('4', calendar.day_name[4]),
		('5', calendar.day_name[5]),
		('6', calendar.day_name[6]),
	], 'Day', required=True)
				   
	@api.depends('timing_id','subject_id','subject_type','hours')
	def _compute_end_time(self):
		for rec in self:
			credit_hours = 0
			minutes = 0.0
			curriculum_id = self.env['uni.faculty.curriculum'].search([('batch_id','=',rec.batch_id.id)])
			curriculum_line_id = self.env['uni.faculty.curriculum.line'].search([('level_id','=',rec.level_id.id),('semester_id','=',rec.semester_id.id),('subject_id','=',rec.subject_id.id),('curriculum_id','=',curriculum_id.id)],limit=1)					
			if rec.subject_id and rec.timing_id and rec.subject_type:
				credit_hours = rec.timing_id.duration
				if rec.timing_id.minute != '00':
					if rec.timing_id.minute == '15':
						minutes = .25
					elif rec.timing_id.minute == '30':
						minutes = .5
					elif rec.timing_id.minute == '45':
						minutes = .75

				rec.end_time = rec.hours + float(rec.timing_id.hour)+minutes

	@api.onchange('program_id','semester_id','level_id','batch_id','academic_year_id')
	def onchange_program_id(self):
		domain = {}
		subjects = []
		groups = []
		curriculum_subjects_line_id = self.env['curriculum.subjects.line']
		self.subject_id = False
		self.subject_groups = False
		''' Subject Domain '''
		curriculum_id = self.env['uni.faculty.curriculum'].search([('program_id','=',self.program_id.id),('batch_id','=',self.batch_id.id)],limit=1)
		if curriculum_id:
			curriculum_subjects_line_id = self.env['curriculum.subjects.line'].search([('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('program_id','=',self.program_id.id),('curriculum_id','=',curriculum_id.id)],limit=1)
		else:
			curriculum_subjects_line_id = self.env['curriculum.subjects.line'].search([('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('program_id','=',self.program_id.id)],limit=1)

		subjects = curriculum_subjects_line_id.subject_ids.ids
		
		''' Group Domain '''
		group_ids = self.env['uni.student.groups'].search([('program_id','=',self.program_id.id),('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('batch_id','=',self.batch_id.id),('academic_year_id','=',self.academic_year_id.id)]).ids
		

		domain = {
			'domain':{
			'subject_id':[('id','in',subjects)],
			'subject_groups':[('id','in',group_ids)]
			}
		}
	   
		return domain

	@api.onchange('subject_id','subject_type')
	def onchange_subject(self):
		classroom_lab = []

		classroom_ids = self.env['uni.faculty.classroom'].search([('class_type','=','classroom')])
		lab_ids = self.env['uni.faculty.classroom'].search([('class_type','=','lab')])
		
		curriculum_line_id = self.env['uni.faculty.curriculum.line']
		curriculum_id = self.env['uni.faculty.curriculum'].search([('program_id','=',self.program_id.id),('batch_id','=',self.batch_id.id)],limit=1)
		self.hours = self.timing_id.duration
		
		if curriculum_id:
			curriculum_line_id = self.env['uni.faculty.curriculum.line'].search([('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('curriculum_id','=',curriculum_id.id),('subject_id','=',self.subject_id.id)],limit=1)
		else:
			curriculum_line_id = self.env['uni.faculty.curriculum.line'].search([('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('subject_id','=',self.subject_id.id)],limit=1)

		if self.subject_type == 'practical':
			classroom_lab = [lab.id for lab in lab_ids]
			if curriculum_line_id:
				self.hours = curriculum_line_id.practical_credit_hours
		elif self.subject_type == 'theoretical':
			classroom_lab = [room.id for room in classroom_ids]
			if curriculum_line_id:
				self.hours = curriculum_line_id.theoretical_credit_hours

		self.teacher_id = curriculum_line_id.teacher_id.id

		return {'domain': {'classroom_id': [('id', 'in',  classroom_lab)]}}