from odoo import api, fields, models, _


class res_company(models.Model):
    _inherit = 'res.company'

    fees_income_account = fields.Many2one(
        'account.account', string='Income Fees Account')

    reg_income_account = fields.Many2one(
        comodel_name='account.account', string='Registrtion Fees Account')

    discount_account = fields.Many2one(
        'account.account', string='Student Discount Account')

    receivable_fees_account = fields.Many2one(
        'account.account', string='Receivable Fees Account')


class config_setting(models.TransientModel):
    _inherit = 'res.config.settings'

    fees_income_account = fields.Many2one(
        comodel_name='account.account',
        string='Income Fees Account', related='company_id.fees_income_account', readonly=False)
    
    reg_income_account = fields.Many2one(
        comodel_name='account.account',
        string='Registrtion Fees Account', related='company_id.reg_income_account', readonly=False)

    discount_account = fields.Many2one(
        comodel_name='account.account',
        string='Student Discount Account', related='company_id.discount_account', readonly=False)

    receivable_fees_account = fields.Many2one(
        comodel_name='account.account',
        string='Receivable Fees Account', related='company_id.receivable_fees_account', readonly=False)
