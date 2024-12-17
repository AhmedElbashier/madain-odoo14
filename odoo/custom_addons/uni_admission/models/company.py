# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class res_company(models.Model):
    _inherit = "res.company"

    registration_fees_account_id = fields.Many2one('account.account',)

    tuition_fees_account_id = fields.Many2one('account.account')

    journal_id = fields.Many2one(
        string="Fees Journal",
        comodel_name="account.journal",
        domain="[('type', '=', 'sale')]",
    )

    last_year_code = fields.Char()

    fees_increse_percenatge = fields.Integer(default=10)

    admission_steps_ids = fields.One2many('admission.steps.directions', 'company_id')

    registration_steps_ids = fields.One2many('registration.steps.directions', 'company_id')

    guidelines_financial_management  = fields.One2many('guidelines.financial.management', 'company_id')

    practical_hours = fields.Integer('Practical hours per 1 creadit hours')

class account_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    registration_fees_account_id = fields.Many2one('account.account', related='company_id.registration_fees_account_id', readonly=False,)

    tuition_fees_account_id = fields.Many2one('account.account', related='company_id.tuition_fees_account_id', readonly=False,)

    journal_id = fields.Many2one(
        string="Fees Journal",
        comodel_name="account.journal",
        related='company_id.journal_id',
        domain="[('type', '=', 'sale')]",
        readonly=False,
    )

    fees_increse_percenatge = fields.Integer(related='company_id.fees_increse_percenatge', readonly=False)

    practical_hours = fields.Integer(related='company_id.practical_hours', string='Practical hours per 1 creadit hours', readonly=False,)


class AdStepsDirection(models.Model):
    _name = 'admission.steps.directions'

    name = fields.Char('Step')
    company_id = fields.Many2one('res.company')

class RegStepsDirection(models.Model):
    _name = 'registration.steps.directions'

    name = fields.Char('Step')
    company_id = fields.Many2one('res.company')


class guidelinesFinance(models.Model):
    _name = 'guidelines.financial.management'

    name = fields.Char('Guide')
    company_id = fields.Many2one('res.company')
