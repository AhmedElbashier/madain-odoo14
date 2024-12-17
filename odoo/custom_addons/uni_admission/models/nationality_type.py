# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class NationalityType(models.Model):
    _name = 'uni.nationality.type'
    _description = 'Nationality Type'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True)

    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True
    )

    active = fields.Boolean(string="Active", default=True)

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            obj = self.search([('name','=ilike',record.name),('id','!=',record.id)])
            if obj:
                raise ValidationError(_("There is another national type with the same name: %s" % record.name))
