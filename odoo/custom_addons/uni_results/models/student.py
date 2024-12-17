
from odoo import api, fields, models, _


class Student(models.Model):
	_inherit = 'uni.student'


	result_ids = fields.One2many('marksheet.line', 'student_id')
	# study_year_no = fields.Integer()
	seeting_number = fields.Char('Setting Number')
	

class Program(models.Model):
    _inherit = 'uni.faculty.program'

    maximum_study_years = fields.Integer()
