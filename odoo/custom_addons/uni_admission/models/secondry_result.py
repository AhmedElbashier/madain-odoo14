from odoo import api, fields, models, _

class result(models.Model):
	_name = 'secondary.result'

class brother_details(models.Model):
	_name = 'brother.details'

	name = fields.Char('Name')
	level_id = fields.Many2one('uni.faculty.level' , string="Level")
	admission_id = fields.Many2one('uni.admission')

class student_result(models.Model):
	_name = 'student.result'

	name = fields.Char(string="Subject")

	degree = fields.Char('Degree')

	admission_id = fields.Many2one('uni.admission')