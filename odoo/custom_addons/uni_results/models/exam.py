# -*- coding: utf-8 -*-

from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import math

class Exam(models.Model):
	_name = "exam.exam"
	_inherit = "mail.thread"
	_description = "Exam"

	record_id = fields.Many2one('uni.exam.record', 'Exam Record',
								 domain=[('state', 'not in',
										  ['done'])], required=True)
   
	subject_id = fields.Many2one('uni.faculty.subject', 'Subject', required=True)
	teacher_id = fields.Many2one('hr.employee')
	attendees_line = fields.One2many(
		'exam.attendees', 'exam_id', 'Attendees',domain=[('main','!=',False)])
	deprived_student_ids = fields.Many2many(
		'uni.student.exam','exam_exam_rel_deprived_student', string='Deprived Students')
	state = fields.Selection(selection=[('draft', 'Draft'), ('schedule', 'Scheduled'), ('held', 'Held'),
		 ('result_updated', 'Result Updated'),
		 ('cancel', 'Cancelled'), ('done', 'Done')],
	   default='draft')
	note = fields.Text('Note')
	name = fields.Char('Name')
	active = fields.Boolean(default=True)
	academic_year_id = fields.Many2one(
		'uni.year', 'Academic Year', related="record_id.academic_year_id",store=True)
	program_id = fields.Many2one(
		'uni.faculty.program', 'Program', related="record_id.program_id",store=True)
	batch_id = fields.Many2one(
		'uni.faculty.department.batch', 'Batch', related="record_id.batch_id",store=True)
	level_id = fields.Many2one(
		'uni.faculty.level', 'Level', related="record_id.level_id",store=True)
	semester_id = fields.Many2one(
		'uni.faculty.semester', "Term", related="record_id.semester_id",store=True)
	exam_date = fields.Date()
	forms_count = fields.Integer(compute="_get_forms_count")
	start_timing_id = fields.Many2one('op.timing', 'Start')
	exam_duration = fields.Float('Duration')
	end_time = fields.Char(compute="_get_end_time")

	full_degree = fields.Float(string="Full Mark")
	success_degree = fields.Float(string="Pass Mark")
	degree_component = fields.One2many('subject.degree.component','exam__id')
	attendance = fields.Boolean(compute="_get_component")
	year_works = fields.Boolean(compute="_get_component")
	practical = fields.Boolean(compute="_get_component")
	final_exam = fields.Boolean(compute="_get_component")
	company_id = fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
	

	_sql_constraints = [
	   ('unique_time', 'unique (program_id,level_id,semester_id,batch_id,exam_date,start_timing_id,exam_duration)',
	   "Sorry.. This batch has another Exam in this Time")
	]

	# @api.constrains('degree_component','degree_component.percentage','degree_component.exam__id','degree_component.curriculum_id')
	# def check_component(self):
	# 	count = 0
	# 	for component in self.degree_component:
	# 		count += component.percentage
	# 	if count != 100:
	# 		raise ValidationError(_(
	# 			"Sorry, the total percentage of component should be 100"))

	@api.depends('start_timing_id','exam_duration')
	def _get_end_time(self):
		for rec in self:
			start = int(rec.start_timing_id.hour)  + int(rec.start_timing_id.minute)/ 60 
			rec.end_time = start + rec.exam_duration


	@api.onchange('start_timing_id')
	def _get_duration(self):
		for rec in self:
			rec.exam_duration = rec.start_timing_id.duration

	def _get_forms_count(self):
		for rec in self:
			rec.forms_count = self.env['exam.template'].search_count([
				('exam_id','=',rec.id)
			])

	@api.depends('degree_component')
	def _get_component(self):
		for rec in self:
			rec.attendance = False
			rec.year_works = False
			rec.practical = False
			rec.final_exam = False
			if rec.degree_component:
				for degree in rec.degree_component:
					if degree.component_type == 'attendance':
						rec.attendance = True
					if degree.component_type == 'year_works':
						rec.year_works = True
					if degree.component_type == 'practical':
						rec.practical = True
					if degree.component_type == 'final_exam':
						rec.final_exam = True				


	@api.onchange('exam_date')
	def onchange_exam_date(self):
		############# Get Justified Absence #############
		if self.attendees_line and self.exam_date:
			for attendee in self.attendees_line:
				############## substitutions request ##############
				attendee_substitutions = self.env['substitution.service'].search([
					('student_id','=',attendee.student_id.id),
					('service_type_id.service_type','=','substitutions'),
					('request_date','=',self.exam_date),
					('state','=','done')
				])
				############## travel permission ##############
				attendee_travel = self.env['uni.student.permissions'].search([
					('name','=',attendee.student_id.id),
					('service_type_id.service_type','=','travel_permission'),
					('start_date','<=',self.exam_date),('end_date','>=',self.exam_date)
					,('state','=','done')
				])
				############## Medical request ##############
				attendee_medical = self.env['uni.student.permissions'].search([
					('name','=',attendee.student_id.id),
					('service_type_id.service_type','=','medical_ornaic'),
					('start_date','<=',self.exam_date),('end_date','>=',self.exam_date),
					('state','=','done')
				])

				if attendee_substitutions or attendee_travel or attendee_medical:
					attendee.status = 'justified_absence'
				else:
					attendee.status = 'presence'

	def _get_deprived_stds(self):
		if self.company_id.attendance_perc:
			attend_percentage = self.company_id.attendance_perc
			time_table = self.env['generate.time.table'].search([
				('batch_id','=',self.batch_id.id),('program_id','=',self.program_id.id),
				('academic_year_id','=',self.academic_year_id.id),
				('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id)],limit=1)

			if time_table:
				sessions = self.env['op.session'].search([('generation_id','=',time_table.id),('subject_id','=',self.subject_id.id)])
				deprived_std_ids = []
				if sessions:
					subject_sessions = len(sessions)
					for std in self.attendees_line:
						counter = 0.0
						for session in sessions:
							for attendee in session.session_attendees_ids:
								if std.student_id.id == attendee.student_id.id:
									if attendee.status in ('presence','justified_absence'):
										counter += 1

						std_percentage = (counter / subject_sessions) * 100
						if std_percentage < attend_percentage and std.student_id.state == 'student':
							deprived_std = self.env['uni.student.exam'].search([('student_id','=',std.student_id.id)])
							
							if deprived_std:
								deprived_std.is_deprived = True
								deprived_std.exam_reason = False
								deprived_std.deprived_reason = 'Low Attendance'
							else:
								deprived_std = self.env['uni.student.exam'].create({
									'student_id':std.student_id.id,
									'seeting_number':0.0,
									'is_deprived': True,
									'deprived_reason':'Low Attendance'
								})
							deprived_std_ids.append(deprived_std.id)
					
						students = []
						for line in self.attendees_line:
							deprived_ids = self.env['uni.student.exam'].browse(deprived_std_ids)
							if line.student_id.id not in deprived_ids.mapped('student_id').ids:
								students.append(line.id)

						self.write({
							'attendees_line':[(6,0,students)],
							'deprived_student_ids':[(6,0,deprived_std_ids)]
						})

	@api.onchange('subject_id')
	def onchange_subject(self):
		teachers = []
		teachers = [teacher.id for teacher in self.subject_id.teacher_ids]
	  
		return {'domain': {'teacher_id': [('id', 'in',  teachers)]}}

	@api.onchange('record_id')
	def onchange_record_id(self):
		self.attendees_line = False
		subjects = []
		subject_ids = [subject.id for subject in self.record_id.subject_ids]
		for student in self.record_id.student_ids:
			self.attendees_line =  [([0,0,{
				'student_id':student.id,
				'seeting_number':'0',
				}])]

		return {'domain': {'subject_id': [('id', 'in',subject_ids)]}}
 
	@api.constrains('full_degree', 'success_degree')
	def _check_marks(self):
		if self.full_degree <= 0.0 or self.success_degree <= 0.0:
			raise ValidationError(_('Enter proper marks!'))
		if self.success_degree > self.full_degree:
			raise ValidationError(_(
				"Passing Marks can't be greater than Total Marks"))

	def exam_template_tree_view(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Exam Form',
			'view_mode': 'tree,form',
			'res_model': 'exam.template',
			'domain': [('exam_id', '=', self.id)],
			'context': {'default_exam_id': self.id},
			
		}


	def act_result_updated(self):
		self.state = 'result_updated'

	def act_schedule(self):
		self.state = 'schedule'

	def act_done(self):
		if self.deprived_student_ids:
			attendees_line = []
			for student in self.deprived_student_ids:
				attendees_line.append(
					([0,0,{
						'student_id':student.student_id.id,
						'seeting_number':student.seeting_number,
						'university_id':student.university_id,
					}])
				)
			self.write({
				'attendees_line':attendees_line
				})
		self.state = 'done'

	def act_draft(self):
		if self.deprived_student_ids:
			ids = []
			for attend in self.attendees_line:
				for student in self.deprived_student_ids:
					if attend.student_id.id == student.student_id.id:
						pass
					else:
						ids.append(attend.id)
			self.write({
			'attendees_line':[(6,0,ids)]
			})
		self.state = 'draft'

	def act_cancel(self):
		self.state = 'cancel'

	@api.model
	def create(self, values):
		res = super(Exam, self).create(values)
		return res


class ExamTemplate(models.Model):
	_name = "exam.template"
	_inherit = "mail.thread"
	_description = "Exam Template"


	# name = fields.Char(required=True)
	exam_template_type = fields.Selection([
		('primary','Primary'),
		('substitutional','Substitutional'),
		('supplement','Supplement'),
		('removal','Removal'),
		], required=True)
	received_date = fields.Date()
	exam_id = fields.Many2one('exam.exam')
	state = fields.Selection([
		('not_received','Not Received'),
		('received','Received'),
		('print_form','Print Form'),
		('subject_professor_approval','Subject professor Approval'),
		('exam_papers_printing','Exam Papers Printing'),
		('packing_exam_papers','Packing Exam Papers'),
		('done','Done'),
		], default='not_received')

	def attachment_tree_view(self):
		action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
		action['domain'] = str([
			('res_model', '=', 'exam.template'),
			('res_id', 'in', self.ids)
			
		])
		action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
		return action


	def act_received(self):
		self.state = 'received'
		self.received_date = date.today()

	def act_print_form(self):
		self.state = 'print_form'

	def act_subject_professor_pproval(self):
		self.state = 'subject_professor_approval'

	def act_exam_papers_printing(self):
		self.state = 'exam_papers_printing'

	def act_packing_exam_papers(self):
		self.state='packing_exam_papers'

	def act_done(self):
		self.state = 'done'


