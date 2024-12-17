# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Disease(models.Model):
    _name = 'uni.health_service.disease'
    _description = 'Disease'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description')
    endemic = fields.Boolean(string='Endemic')
