import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StudentMarks(models.Model):
    _name = "student.exam.mark"

    seat = fields.Char("Seat")
    name = fields.Char("name")
    primary = fields.Float("Primary")
    alt = fields.Float("Alternative")
    add = fields.Float("Additional")
    remove = fields.Float("Remove Fail")
    program = fields.Char("Program")
    subject = fields.Char("Subject")
    uni_id = fields.Char("University ID")


class SubjectMock(models.Model):
    _name = "mock.subject"

    sem = fields.Integer("Sem")
    program = fields.Char("Program")
    name = fields.Char("name")
    code = fields.Char("code")


class UniSubject(models.Model):
	_inherit = 'uni.faculty.subject'

	def name_get(self):
		result = []
		for X in self:
			name = ( X.code + '-' or "") + X.name
			result.append((X.id, name))
		return result