
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class grade_conf(models.Model):
	_name = 'grade.conf'
	_inherit = ['mail.thread']

	name = fields.Char()
	category_ids = fields.One2many('grade.category','grade_id')
	

class grade_category(models.Model):
	_name = 'grade.category'
	_rec_name = 'grade'

	minimum_degree = fields.Float('Minimum Mark')
	maximum_degree = fields.Float('Maximum Mark')
	grade_letter = fields.Char(string="Result to Display")
	grade = fields.Char()
	is_failure = fields.Boolean('Is failure ?')
	grade_id = fields.Many2one('grade.conf')


class config_setting(models.TransientModel):
	_inherit = 'res.config.settings'

	level_grade = fields.Many2one('grade.conf', related='company_id.level_grade', readonly=False)
	semester_grade = fields.Many2one('grade.conf', related='company_id.semester_grade', readonly=False)
	subject_grade = fields.Many2one('grade.conf', related='company_id.subject_grade', readonly=False)
	gpa_grade = fields.Many2one('grade.conf', related='company_id.level_grade', readonly=False)
	attendance_perc = fields.Float(
        string='Attendance Deprive Minumum Percentage(%)', related="company_id.attendance_perc",readonly=False)
	recorrection_period = fields.Integer('Recorrection Period', related='company_id.recorrection_period', readonly=False)

class Company(models.Model):
	_inherit = 'res.company'

	level_grade = fields.Many2one('grade.conf')
	semester_grade = fields.Many2one('grade.conf')
	subject_grade = fields.Many2one('grade.conf')
	gpa_grade = fields.Many2one('grade.conf')
	attendance_perc = fields.Float(
        string='Attendance Deprive Minumum Percentage(%)', readonly=False)
	recorrection_period = fields.Integer('Recorrection Period')
   