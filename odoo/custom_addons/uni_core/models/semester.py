from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class Semester(models.Model):
    _name = 'uni.faculty.semester'
    _inherit = ['mail.thread']
    _description = "Term"
    # _rec_name = 'order'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char('Code', required=True )
    # TODO : add order to specific group (acdmic adminstration), selection
    order = fields.Selection(string='Order', selection=[
        ('1', "1"),
        ('2', "2"),
        ('3', "3"),
        ('4', "4"),
        ('5', "5"),
        ('6', "6"),
        ('7', "7"),
        ('8', "8"),
        ('9', "9"),
        ('10', "10"),
        ('11', "11"),
        ('12', "12"),
    ],
        required=True
    )

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        # domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        string='Faculty',
        required=True
    )

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            semester_id = self.env['uni.faculty.semester'].search(['|',('name','=ilike',record.name),('code','=ilike',record.code),('id','!=',record.id)],limit=1)
            semester_order = self.env['uni.faculty.semester'].search([('order','=ilike',record.order),('id','!=',record.id)],limit=1)
            if semester_id:
                raise ValidationError(_("There is another semester with the same name or code: %s" % semester_id.name))
            if semester_order:
                raise ValidationError(_("There is another semester with the same order: %s" % semester_order.name))
