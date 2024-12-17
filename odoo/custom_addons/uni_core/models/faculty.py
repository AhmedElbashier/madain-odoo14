# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class Faculty(models.Model):
    _inherit = 'res.company'

    department_ids = fields.One2many(
        string="Departments",
        comodel_name="uni.faculty.department",
        inverse_name="faculty_id",
        readonly=True
    )
    
