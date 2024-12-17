# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class admission_statistical(models.TransientModel):
    _name = 'admission.statistical.wizard'

    year_id = fields.Many2one(
        string="Academic Year",
        comodel_name="uni.year",
        required=True,
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
            ['year_id', 'admission_category_id'])[0]
        return self.env['report'].get_action(self, 'uni_admission.admission_statistical', data=data)
