# -*- coding: utf-8 -*-
##############################################################################
#
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import models, fields, api, _

class Punishment(models.Model):
	_name = 'punishment.type'
	_inherit = ['mail.thread']
	_rec_name = 'name'

	name = fields.Char('Name')
	sequence = fields.Char('Order')
	violation_id = fields.Many2one('violation.type')
	
