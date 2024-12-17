from odoo import api, fields, models, _

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        move_ids = self.env['account.move'].browse(self._context.get('active_ids', []))
        for move in move_ids:
            if move.payment_state == 'paid' and move.installment_id.first_installment:
                move.installment_id.registration_request_id.student_id.write({
                    'registration_status':'registered',
                    })
        return res
class AccountMove(models.Model):
    _inherit = 'account.move'

    installment_id = fields.Many2one(
        string="Request",
        comodel_name="uni.fees.installment",
    )

    student_id = fields.Many2one('uni.student', related='installment_id.registration_request_id.student_id')

    program_id = fields.Many2one('uni.faculty.program',related='student_id.program_id')

    level_id = fields.Many2one('uni.faculty.level', related='student_id.level_id')

    invoice_type = fields.Selection([('first_installment_reg','First Installment + Registration'),('second_installment','Second Installment')], compute='_compute_invoice_type')

    @api.depends('installment_id')
    def _compute_invoice_type(self):
        for rec in self:
            if rec.installment_id.first_installment and rec.installment_id.include_registration_fees:
                rec.invoice_type = 'first_installment_reg'
            else:
                rec.invoice_type = 'second_installment'

    def _compute_payments_widget_to_reconcile_info(self):
        res = super(AccountMove, self)._compute_payments_widget_to_reconcile_info()
        for move in self:
            if move.payment_state == 'paid' and move.installment_id.first_installment:
                move.installment_id.registration_request_id.student_id.write({
                    'registration_status':'registered',
                    })

    def button_draft(self):
        super(AccountMove, self).button_draft()
        return True

       
