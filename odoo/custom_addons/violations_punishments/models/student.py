# -*- coding: utf-8 -*-
##############################################################################
#
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import models, fields, api, _

class Students(models.Model):
	_inherit = 'uni.student'

	violations_count= fields.Integer('Violations Count', compute="_compute_violation")

	def show_violations(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Student Violations',
			'view_mode': 'tree,form',
			'res_model': 'student.violation',
			'domain': [('student_id', '=', self.id)],
			'context': {'default_student_id': self.id},
			
		}
	   
	def _compute_violation(self):
		for rec in self:
			vl_count=self.env['student.violation'].search_count([('student_id','=',self.id)])
			rec.violations_count = vl_count
