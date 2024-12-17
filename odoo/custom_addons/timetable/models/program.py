# -*- coding: utf-8 -*-

from odoo import models, fields


class Batch(models.Model):
    _inherit = "uni.faculty.department.batch"

    session_ids = fields.One2many('op.session', 'faculty_id', 'Sessions')
