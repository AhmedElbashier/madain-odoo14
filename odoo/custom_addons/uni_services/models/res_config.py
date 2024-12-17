
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class config_setting(models.TransientModel):
	_inherit = 'res.config.settings'

	service_journal_id = fields.Many2one(
        string="Service Journal",
        comodel_name="account.journal",
        related='company_id.service_journal_id',
        domain="[('type', '=', 'sale')]",
        readonly=False,
    )

	
class Company(models.Model):
	_inherit = 'res.company'

	service_journal_id = fields.Many2one(
        string="Service Journal",
        comodel_name="account.journal",
        domain="[('type', '=', 'sale')]",
    )

