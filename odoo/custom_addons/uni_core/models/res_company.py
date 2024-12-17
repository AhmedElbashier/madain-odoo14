from odoo import api, fields, models , _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class res_company(models.Model):
    _inherit = 'res.company'
    _description = 'Company'

    name = fields.Char(related='partner_id.name', string='Faculty Name', required=True, store=True, readonly=False)

    code = fields.Char(string='Faculty Code', required=True, translate=True)

    last_std_no = fields.Integer('Last Student No.', required=True)