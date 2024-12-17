# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class registration_statistics(models.TransientModel):
    _name = 'uni_admission.registration_statistics.wizard'

    def check_report(self, data):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        return self.env['report'].get_action(self, 'uni_admission.registration_statistics_report', data=data)
