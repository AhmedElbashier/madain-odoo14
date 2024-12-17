# -*- encoding: utf-8 -*-

from odoo import api, fields, models,_


class Company(models.Model):
    _inherit = 'res.company'


    name = fields.Char(
    related='partner_id.name',
    string='Name',
    required=True,
    store=True,
    translate=True
    )
    # registration_fee_increase = fields.Float(string="Registration Fee Increase")