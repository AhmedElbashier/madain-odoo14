
from odoo import api, fields, models
from odoo.exceptions import ValidationError


# class LateRegistration(models.Model):
#     _name = 'uni.late.registration'

#     name = fields.Many2one('uni.student', string="Name/Universit Id/Student NO", required=True)

#     code = fields.Char(string='Code', readonly=True)

#     request_date = fields.Date('Request Date', required=True, default=fields.Date.today())

#     program_id = fields.Many2one(
#         string="Program",
#         comodel_name="uni.faculty.program",
#         required=True,
#     )

#     level_id = fields.Many2one(
#         string="Level",
#         comodel_name="uni.faculty.level",
#         required=True,
#     )

#     semester_id = fields.Many2one(
#         string="Term",
#         comodel_name="uni.faculty.semester",
#         required=True,
#     )

#     academic_status = fields.Selection(
#         string="Acadimic Status",
#         selection=[
#             ('fresh', 'Fresh'),
#             ('success', 'Success'),
#             ('repeat', 'Repeat'),
#             ('appendix' , 'Has Appendixs'),
#             ('substitutions', 'Has Substitutions'),
#         ],
#         default='fresh',required=True
#     )

#     coordinator_recommendation = fields.Text('Coordinator Recommendation')

#     scientific_affairs_recommendation = fields.Text('Scientific Affairs Recommendation')

#     dean_decision = fields.Text('Dean Decision')

#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('requested', 'Requested'),
#         ('under_payment','Under Payment'),
#         ('paid','Paid'),
#         ('coordinator','Coordinator'),
#         ('scientific_affairs','Scientific Affairs'),
#         ('dean_decision','Dean decision'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ],default="draft")

#     @api.onchange('name')
#     def onchange_student(self):
#         self.program_id = self.name.program_id.id,
#         self.level_id = self.name.level_id.id
#         self.semester_id = self.name.semester_id.id
#         self.academic_status = self.name.academic_status


#     def action_request(self):
#         self.state = 'requested'

#     def action_approve(self):
#         self.state = 'approved'

#     def action_reject(self):
#         self.state = 'rejected'

#     def rest_draft(self):
#         self.state = 'draft'

#     def action_confirm(self):
#         # invoice_id = self.env['account.move'].create({
#         #     'partner_id':self.name.partner_id.id,
#         #     'invoice_date':date.today(),
#         #     'move_type':'out_invoice',

#         #     })
#         # invoice_line_id = self.env['account.move.line'].create({
#         #     'name':'Late Registration',
#         #     'price_unit':5000,
#         #     'price_subtotal':5000,
#         #     'account_id':21,
#         #     'move_id':invoice_id.id
#         #     })
#         #invoice_id.action_post()
#         self.state = 'under_payment'

#     def action_payment(self):
#         self.state = 'paid'

#     def action_coordinator(self):
#         self.state = 'coordinator'

#     def action_scientific_affairs(self):
#         self.state = 'scientific_affairs'

#     def action_dean_decision(self):
#         self.state = 'dean_decision'


#     @api.model
#     def create(self, values):
#         values['code'] =self.env['ir.sequence'].next_by_code('uni.late.registration') or '/'

#         return super(LateRegistration, self).create(values)


class SubjectSchedule(models.Model):
    _name = 'uni.subject.schedule'

    name = fields.Char('Name')

    day = fields.Selection([
        ('saturday','Saturday'),
        ('sunday','Sunday'),
        ('monday','Monday'),
        ('tuesday','Tuesday'),
        ('wednesday','Wednesday'),
        ('thursday','Thursday'),
        ])