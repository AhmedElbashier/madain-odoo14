from odoo import api, fields, models


class Students(models.Model):
    _name = 'uni.card'
    _rec_name = 'student_id'

    state = fields.Selection([('draft','Draft'),('wait_payment', 'Wait Payment'),('wait_print', 'Wait Printing'),('wait_delivery', 'Waiting Delivery'),('done','Done'),('cancel', 'Cancel')], string="Status")
    source = fields.Selection([('addmission','Addmission'), ('lost', 'Replacement of lost Request'), ('damaged', 'Damaged Replacement Request'),('done','Done')], string="Source")
    cancel_reason = fields.Text('Cancel Reason')
    number = fields.Char('Card Number')
    print_date = fields.Date("Printing Date")
    deliver_date = fields.Date("Delivering Date")
    student_id = fields.Many2one('uni.student', string="Student")
    card_service_id = fields.Many2one('uni.general.services')


    def action_delivery(self):
        self.card_service_id.printing_date = self.print_date
        self.state = 'wait_delivery'

    def action_done(self):
        self.card_service_id.delivery_date = self.deliver_date
        self.state = 'done'