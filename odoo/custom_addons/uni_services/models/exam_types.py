from odoo import api, fields, models
from odoo.addons.uni_core.utils import get_default_faculty
from odoo.tools.translate import _

class ExamTypes(models.Model):
    _name = 'uni.exam.types'
    _description = 'Exam Types'
    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, translate=True)
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        (
            'name_unique',
            'UNIQUE(name)',
            _("The exam's type name must be unique")
        ),
    ]
