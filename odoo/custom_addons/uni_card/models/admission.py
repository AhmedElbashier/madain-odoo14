from odoo import api, fields, models


class Admission(models.Model):
    _inherit = 'uni.admission'


    def create_student_record(self):
        res = super(Admission, self).create_student_record()
        self.create_card_request(self.student_id)
        return res


    def create_card_request(self,student):
        card_id = self.env['uni.card'].create({
            'student_id':student.id,
            'source':'addmission',
            'state':'wait_payment',
            })


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        move_ids = self.env['account.move'].browse(self._context.get('active_ids', []))
        for move_id in move_ids:
            if move_id.service_id:
                if move_id.service_id.service_type_id.service_type == 'card_lost':
                    card_id = self.env['uni.card'].search([('student_id','=',move_id.service_id.student_id.id),('source','in',['lost','damaged']),('card_service_id','=',move_id.service_id.id)],limit=1)
                    if card_id:
                        card_id.write({'state':'wait_print'})
            if move_id.payment_state == 'paid' and move_id.installment_id.first_installment:
                move_id.installment_id.registration_request_id.student_id.write({
                    'registration_status':'registered',
                    })
                card_id = self.env['uni.card'].search([('student_id','=',move_id.installment_id.registration_request_id.student_id.id),('source','=','addmission')],limit=1)
                if card_id:
                    card_id.write({'state':'wait_print'})
        return res
    