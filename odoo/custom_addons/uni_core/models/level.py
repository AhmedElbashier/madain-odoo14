from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

class Level(models.Model):
    _name = 'uni.faculty.level'
    _inherit = ['mail.thread']
    _description = 'Years'
    # _rec_name = 'order'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    order = fields.Selection(string='Order', selection=[
        ('1', "1"),
        ('2', "2"),
        ('3', "3"),
        ('4', "4"),
        ('5', "5"),
        ('6', "6"),
    ],
        required=True
    )

    @api.constrains('name','code','order')
    def _check_name(self):
        for record in self:
            level_id = self.env['uni.faculty.level'].search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)],limit=1)
            level_order = self.env['uni.faculty.level'].search([('order','=ilike',record.order),('id','!=',record.id)],limit=1)
            if level_id:
                raise ValidationError(_("There is another Level with the same name or code: %s" % level_id.name))
            if level_order:
                raise ValidationError(_("There is another Level with the same order: %s" % level_order.name))

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        # domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        string='Faculty',
        required=True
    )
