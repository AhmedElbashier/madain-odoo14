
from odoo import api, fields, models


class ExamTypes(models.Model):
	_inherit = 'uni.exam.types'
	_description = 'Exam Types'


	exam_category = fields.Selection(selection=[
		('first_round','First round'),
		('second_round','Second round'),
		('third_round','Third round'),
	],default="first_round", translate=True)

	is_substitutionals = fields.Boolean(default=False)
