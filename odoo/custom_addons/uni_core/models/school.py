from odoo import api, fields, models

class UniSchool(models.Model):
    _name = 'uni.school'

    name = fields.Char(string="Secondary School")