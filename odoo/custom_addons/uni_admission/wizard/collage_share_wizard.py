# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class collage_share(models.TransientModel):
    _name = "collage.share.wizard"

    start = fields.Date(string="From", )
    end = fields.Date(string="To", )

    def check_report(self, data):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['start', 'end'])[0]
        return self.env['report'].get_action(self, 'collage_share.report', data=data)
