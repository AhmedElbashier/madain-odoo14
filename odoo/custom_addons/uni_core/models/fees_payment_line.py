from odoo import api, fields, models


class payment_line(models.Model):
    _name = 'fees.payment.line'

    level_id = fields.Many2one(
        'uni.faculty.level',
        string='Level',
        readonly=True
    )

    semester_id = fields.Many2one(
        'uni.faculty.semester',
        string="Term",
        readonly=True
    )

    amount = fields.Float('Amount')

    payment_date = fields.Date('Payment date')

    payment_type = fields.Selection(
    	[('cash','Cash'),
    	('bank','Bank'),
    	('check','Check'),
    	('transfer','Bank Transfer')],
    	'Payment Type',default='cash',required=True
    	)
    currency_id = fields.Many2one('res.currency',string="Currency")

    fees_id = fields.Many2one('student.fees')

    student_id = fields.Many2one('uni.student')

    check_number = fields.Char('Check Number')

    account_number = fields.Char('Account Number')