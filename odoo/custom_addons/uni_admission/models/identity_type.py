# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class NationalityType(models.Model):
    _name = 'uni.identity.type'
    _description = 'Identity Type'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True)