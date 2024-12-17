from odoo import api, fields, models


class Student(models.Model):
    _inherit = 'uni.student'

    medical_record = fields.Many2one(
        string="Medical Record",
        comodel_name="uni.student",
        ondelete="cascade"
    )
