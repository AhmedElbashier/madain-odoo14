from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

class Department(models.Model):
    _name = 'uni.faculty.department'
    _inherit = ['mail.thread']
    _description = 'Department'

    name = fields.Char(string='Name', required=True, translate=True)

    code = fields.Char(string="Code", required=True)

    faculty_id = fields.Many2one(
        comodel_name='res.company',
        # domain="[('type', '=', 'faculty')]",
        string='Faculty',
        default=lambda self: get_default_faculty(self),
        required=True
    )

    specialization_ids = fields.One2many(
        comodel_name='uni.faculty.department.specialization',
        inverse_name='department_id',
        string='Specializations',
        readonly=True
    )

    branch_id = fields.Many2one(
        string="Branch",
        comodel_name="uni.faculty.branch",
        domain="[('faculty_id', '=', faculty_id)]"
    )

    program_id = fields.Many2one(
        comodel_name='uni.faculty.program',
        string="Program",
        required=True)

    @api.constrains('name','faculty_id')
    def _check_name(self):
        for record in self:
            obj = self.env['uni.faculty.department'].search([
                ('name','=ilike',record.name),
                ('id','!=',record.id)
                ])
            if obj:
                raise ValidationError(_("There is another Department with the same name: %s" % record.name))