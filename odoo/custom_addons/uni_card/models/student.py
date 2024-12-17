from odoo import api, fields, models


class Students(models.Model):
    _inherit = 'uni.student'

    card_count = fields.Integer('Card Count', compute="_compute_cards")

    def card_tree_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cards',
            'view_mode': 'tree,form',
            'res_model': 'uni.card',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
            
        }

    def _compute_cards(self):
        for rec in self:
            card_count=self.env['uni.card'].search_count([('student_id','=',self.id)])
            rec.card_count = card_count
