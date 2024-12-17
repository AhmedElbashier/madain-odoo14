from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _


class Branch(models.Model):
    _name = 'uni.faculty.branch'
    _description = 'Branch'

    name = fields.Char(string="Name", translate=True, required=True)

    faculty_id = fields.Many2one(
        string="Faculty",
        comodel_name="res.company",
        # domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        required=True
    )

    department_ids = fields.One2many(
        string="Departments",
        comodel_name="uni.faculty.department",
        inverse_name="branch_id",
        readonly=True
    )

    _sql_constraints = [
        (
            'name_unique',
            'UNIQUE(faculty_id, name)',
            _('The name must be unique')
        ),
    ]
