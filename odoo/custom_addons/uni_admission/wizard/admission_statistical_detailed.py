# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.addons.uni_core.utils import get_default_faculty


class admission_statistical_detailed(models.TransientModel):
    _name = 'admission.statistical.detailed.wizard'
    faculty_id = fields.Many2one(
        comodel_name='res.company',
        string='Faculty',
        domain="[('type', '=', 'faculty')]",
        default=lambda self: get_default_faculty(self),
        required=True
    )

    department_id = fields.Many2one(
        'uni.faculty.department',
        string='Department',
        domain="[('faculty_id', '=', faculty_id)]",
        required=True
    )

    specialization_id = fields.Many2one(
        string="Specialization",
        comodel_name="uni.faculty.department.specialization",
        domain="[('department_id.faculty_id', '=', faculty_id)]",
    )

    level_id = fields.Many2one(
        string="Level",
        comodel_name="uni.faculty.level",
        domain="[('faculty_id', '=', faculty_id)]",
    )

    semester_id = fields.Many2one(
        string="Term",
        comodel_name="uni.faculty.semester",
        domain="[('faculty_id', '=', faculty_id)]",
    )

    admission_category_id = fields.Many2one(
        string="Admission Category",
        comodel_name="uni.student_category",
    )

    def check_report(self, data):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['faculty_id', 'department_id', 'specialization_id', 'level_id', 'semester_id', 'admission_category_id'])[0]
        return self.env['report'].get_action(self, 'uni_admission.admission_statistical_detailed', data=data)
