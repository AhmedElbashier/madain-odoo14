from odoo import api, fields, models


class GeneralServices(models.Model):
    _inherit = 'uni.general.services'

    card_id = fields.Many2one('uni.card')


    def action_confirm(self):
        res = super(GeneralServices, self).action_confirm()
        if self.operation_type == 'lost_card':
            card_id = self.env['uni.card'].create({
                'student_id':self.student_id.id,
                'source':'lost' if self.reason == 'loss' else 'damaged',
                'state':'wait_payment' if self.is_paid else 'wait_print',
                'card_service_id':self.id,
                })

            self.card_id = card_id.id