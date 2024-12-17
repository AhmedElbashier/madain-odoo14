import json
from odoo import api, fields, models, _


class SubjectRecommendations(models.Model):
	_name = 'subject.recommendations.list'
	_inherit = ['mail.thread']


	subject_id = fields.Many2one(
		'uni.faculty.subject',
		)
	
	minimum_degree = fields.Float(
		'Minimum Mark',
		)
	
	extra_degree = fields.Float(
		'Extra Mark',
		)
	
	date = fields.Date(required=True,default=fields.Date.today())
	
	recommenation_type = fields.Selection(
		selection=[
			('program_council','Program Council'),
			('scientific_council','Scientific Council')
		],compute='_compute_recommenation_type',store=True)

	result_id = fields.Many2one(
		'uni.result.record')
	subject_ids = fields.Many2many(
		'uni.faculty.subject',related="result_id.subject_ids")
	absolute = fields.Boolean(default=False,string="Absolute Degree?")

	state = fields.Selection(related='result_id.state')

	@api.depends('state')
	def _compute_recommenation_type(self):
		for rec in self:
			if rec.state == 'program_council_recomm' and not rec.recommenation_type :
				rec.recommenation_type = 'program_council'
			elif rec.state == 'scientific_council_recomm' and not rec.recommenation_type:
				rec.recommenation_type = 'scientific_council'

	def mrk_line_tree_view(self):
		attendance_ids = self.env['exam.attendees']
		if self.recommenation_type == 'program_council':
			attendance_ids = self.env['exam.attendees'].search([('subject','=',self.subject_id.id),('program_council_push', '>', 0)]).ids
			
		else:
			attendance_ids = self.env['exam.attendees'].search([('subject','=',self.subject_id.id),('scientific_council_push', '>', 0)]).ids

		line_ids = self.env['marksheet.line'].search([('marksheet_reg_id','=',self.result_id.marksheet_id.id),('attendees_line','in',attendance_ids)]).ids
		return {
			'type': 'ir.actions.act_window',
			'name': 'Students',
			'view_mode': 'tree,form',
			'res_model': 'marksheet.line',
			'domain': [('id', 'in', line_ids),],
		}


class StudentRecommendations(models.Model):
	_name = 'student.recommendations.list'
	_inherit = ['mail.thread']

	student_id = fields.Many2one(
		'uni.student',
		required=True)

	subject_id = fields.Many2one(
		'uni.faculty.subject')
	
	given_degree = fields.Float(
		'Given Mark',
		required=True)
	
	date = fields.Date(required=True,default=fields.Date.today())
	
	recommenation_type = fields.Selection(
		selection=[
			('program_council','Program Council'),
			('scientific_council','Scientific Council'),
			('recorrection','Recorrection')
		],compute="_compute_recommenation_type",readonly=False,store=True)#compute="_get_default_type",

	result_id = fields.Many2one(
		'uni.result.record')

	recorrection_result_id = fields.Many2one(
		'uni.result.record')

	state = fields.Selection(related="result_id.state")

	state2 = fields.Selection(related="recorrection_result_id.state")

	exam_id = fields.Many2one('uni.exam.record',string='Exam Record', related='result_id.exam_id')

	year_id = fields.Many2one('uni.year',string='Academic Year', related='result_id.year_id')

	subject_ids = fields.Many2many(
		'uni.faculty.subject',related="result_id.subject_ids")

	recorrection_subject_id = fields.Many2one(
		'uni.faculty.subject', string='Subject')

	student_ids = fields.Many2many('uni.student',related="result_id.students")

	student_id_domain = fields.Char(
			compute="_compute_student_id_domain",
			readonly=True,
			store=False,
			)

	@api.depends('state')
	def _compute_recommenation_type(self):
		for rec in self:
			if rec.state == 'program_council_recomm' and not rec.recommenation_type :
				rec.recommenation_type = 'program_council'
			elif rec.state == 'scientific_council_recomm' and not rec.recommenation_type:
				rec.recommenation_type = 'scientific_council'

			elif rec.state2 == 'recorrection_recomm' and not rec.recommenation_type:
				rec.recommenation_type = 'recorrection'
				#rec.update({'recommenation_type':'recorrection'})

	# @api.depends('state')
	# def _get_default_type(self):
	# 	for rec in self:
	# 		if rec.state == 'program_council_recomm':
	# 			rec.update({'recommenation_type':'program_council'})

	# 		if rec.state == 'scientific_council_recomm':
	# 			rec.update({'recommenation_type':'scientific_council'})

	# 		if rec.state2 == 'recorrection_recomm':
	# 			rec.update({'recommenation_type':'recorrection'})

	@api.depends('exam_id','state2')
	def _compute_student_id_domain(self):
		for rec in self:
			student_ids = []
			if rec.state2 == 'recorrection_recomm':
				print('---------------------in ifffffffffff',self.recorrection_result_id)
				recorrection_ids = self.env['uni.student.recorrection'].search([('academic_year_id','=',self.recorrection_result_id.year_id.id),('batch_id','=',self.recorrection_result_id.batch_id.id),('state','=','done')],limit=1)
				print('---------------------recorrection_ids',recorrection_ids)
				student_ids = [rec.student_id.id for rec in recorrection_ids]
				print('---------------------student_ids',student_ids)
			else:
				print('---------------------in elseeeeeeee')
				student_ids = [student.student_id.id for student in rec.exam_id.student_ids]
			
			rec.student_id_domain = json.dumps(
					[('id', 'in', student_ids)]
					)
			print('-------------- student_id_domain')


	@api.onchange('student_id')
	def onchange_student(self):
		domain = {}
		subjects = []
		if self.state2 == 'recorrection_recomm':
			recorrection_ids = self.env['uni.student.recorrection'].search([('student_id','=',self.student_id.id),('academic_year_id','=',self.recorrection_result_id.year_id.id),('state','=','done')],limit=1)
			if recorrection_ids:
				for line in recorrection_ids.subject_ids:
					subjects.append(line.subject_id.id)

		domain = {
			'domain':{
			'recorrection_subject_id':[('id','in',subjects)],
			}
		}
		return domain


