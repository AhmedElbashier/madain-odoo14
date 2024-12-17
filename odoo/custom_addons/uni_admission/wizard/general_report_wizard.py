# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class general_report(models.TransientModel):
    _name = 'uni_admission.general_report.wizard'

    faculty_ids = fields.Many2many(
        comodel_name='res.company',
        string='Faculty',
        relation="gen_re_faculty_rel",
        column1="general_id",
        column2="faculty_id",
        domain="[('type', '=', 'faculty')]",

    )

    department_ids = fields.Many2many(
        string="Departments",
        comodel_name="uni.faculty.department",
        relation="gen_re_deparment_rel",
        column1="general_id",
        column2="department_id",
        #domain="[('faculty_id', 'in', faculty_ids)]",
    )

    specialization_ids = fields.Many2many(
        string="Specialization",
        comodel_name="uni.faculty.department.specialization",
        relation="gen_re_specialization_rel",
        column1="general_id",
        column2="specilization_id",
        #domain="[('faculty_id', 'in', faculty_ids)]",

    )

    level_ids = fields.Many2many(
        string="Levels",
        comodel_name="uni.faculty.level",
        relation="gen_re_level_rel",
        column1="general_id",
        column2="level_id",
        #domain="[('faculty_id', 'in', faculty_ids)]",
    )

    admission_category_ids = fields.Many2many(
        string="Admission Category",
        comodel_name="uni.student_category",
        relation="gen_re_admission_cat_rel",
        column1="general_id",
        column2="cat_id",
    )

    def check_report(self, data):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['faculty_ids', 'department_ids', 'specialization_ids', 'level_ids', 'admission_category_ids'])[0]
        return self.env['report'].get_action(self, 'uni_admission.general_report', data=data)
