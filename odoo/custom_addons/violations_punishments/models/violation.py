# -*- coding: utf-8 -*-
##############################################################################
#
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from calendar import monthrange

num2words = {1: 'First', 2: 'Second', 3: 'Third', 4: 'fourth', 5: 'Fifth', \
			 6: 'Sixth', 7: 'Seventh', 8: 'Eighth', 9: 'ninth', 10: 'Tenth', \
			11: 'Eleventh', 12: 'Twelfth', 13: 'Thirteenth', 14: 'Fourteenth', \
			15: 'Fifteenth', 16: 'Sixteenth', 17: 'Seventeenth', 18: 'Eighteenth', \
			19: 'Nineteenth', 20: 'Twentieth'}


class student(models.Model):
	_inherit = 'uni.student'

	violation_ids = fields.One2many('student.violation','student_id')

class Violation(models.Model):
	_name = 'violation.type'
	_inherit = ['mail.thread']
	_rec_name = 'name'

	name = fields.Char('Name',required=True)
	code = fields.Char('Code',readonly=True)
	has_punishment = fields.Boolean(string='Has Punishment')
	punishment_ids = fields.One2many('punishment.type','violation_id')

	@api.model
	def create(self, vals):
		vals['code'] = self.env['ir.sequence'].next_by_code(
			'violation') or '/'
		res = super(Violation, self).create(vals)
		return res


class StudentViolation(models.Model):
	_name = 'student.violation'
	_inherit = ['mail.thread']
	_rec_name =  'student_id'

	student_id = fields.Many2one('uni.student', domain=[('state','in',['student','frozen'])],required=True)
	program_id = fields.Many2one('uni.faculty.program')
	level_id = fields.Many2one('uni.faculty.level')
	semester_id = fields.Many2one('uni.faculty.semester')
	violation_date = fields.Date('Violation Date', required=True)
	violation_id = fields.Many2one('violation.type','Violation')
	punishment_id = fields.Many2one('punishment.type','Punishment')
	state = fields.Selection([
		('draft','Draft'),
		('done','Done')
	],default='draft')
	time = fields.Char('Violation Time',compute="_compute_time",store=True)
	other_details = fields.Text(string='Other details')
	
	@api.onchange('student_id')
	def onchange_student(self):
		self.program_id = self.student_id.program_id.id,
		self.level_id = self.student_id.level_id.id
		self.semester_id = self.student_id.semester_id.id


	@api.onchange('violation_id','student_id')
	def onchange_violation(self):
		seq = []
		student_violation_ids = self.search([('student_id','=',self.student_id.id),('violation_id','=',self.violation_id.id)])
		if student_violation_ids:
			for violation in student_violation_ids:
				seq.append(violation.punishment_id.sequence)
			last_violation = max(seq)

			punishment_id = self.env['punishment.type'].search([
				('violation_id','=',self.violation_id.id),
				('sequence','>',last_violation)],order='sequence asc',limit=1)
			self.punishment_id = punishment_id.id
		else:
			punishment_id = self.env['punishment.type'].search([
				('violation_id','=',self.violation_id.id)],order='sequence asc',limit=1)
			self.punishment_id = punishment_id.id


	@api.depends('violation_id')
	def _compute_time(self):
		if self.student_id and self.violation_id:
			violation_punishments = self.env['punishment.type'].search([('violation_id','=',self.violation_id.id)])
			std_violations = self.search([('student_id','=',self.student_id.id),('violation_id','=',self.violation_id.id)])
			std_last_punishment = last_punishment = 0

			if violation_punishments:
				punishment_seq = []
				for punish in violation_punishments:
					punishment_seq += [punish.sequence] 
				last_punishment = max(punishment_seq)

				if std_violations:
					std_punishment_seq = []
					for vio in std_violations:
						std_punishment_seq += [vio.punishment_id.sequence] 
					std_last_punishment = max(std_punishment_seq)

					if last_punishment >= std_last_punishment:
						if self.punishment_id:
							self.time = num2words[int(self.punishment_id.sequence)]
						else:
							raise ValidationError(_('Sorry,, This student has consume all punishments on selected violation.'))
	
			else:
				raise ValidationError(_('Sorry,, This violation has no punishments.'))

	def action_confirm(self):
		self.write({'state':'done'})

	