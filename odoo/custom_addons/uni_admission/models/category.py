from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class Category(models.Model):
    _name = 'uni.student_category'
    _description = 'Disccount Category'
    _inherit = ['mail.thread']

    name = fields.Char("Name", required=True)
    general_discount = fields.Float(string="General Discount")
    include_registration_fees = fields.Boolean(
        string="Include Registration Fees")
    discount_type = fields.Selection(string="Discount Type",
        selection=[
        ('regulation','According to the regulation'),
        ('committee','According to the committee'),
        ('other','Other')],
        default='regulation'
        )
    discount_reason = fields.Text(string="Note")
    _sql_constraints = [
        (
            'name_unique',
            'UNIQUE(name)',
            _('The name must be unique')
        ),
    ]

    @api.constrains("general_discount")
    def _check_discounts(self):
        for s in self:
            if s.general_discount < 0 :
                raise ValidationError(_("Discount can't be less than 0%"))

    @api.depends('name', 'general_discount ')
    def name_get(self):

        result = []
        for X in self:
            name = ( X.name + ' - ' or "") + str(X.general_discount)

            result.append((X.id, name)) 
            
        return result