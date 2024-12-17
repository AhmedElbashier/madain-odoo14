from datetime import datetime, date
from odoo import api, fields, models, _



class account_move(models.Model):
    _inherit = 'account.move'

    permission_service_id = fields.Many2one('uni.student.permissions')
    late_registration_service_id = fields.Many2one('uni.late.registration')
    recorrection_service_id = fields.Many2one('uni.student.recorrection')
    substitution_service_id = fields.Many2one('substitution.service')
    fail_removal_service_id = fields.Many2one('fail.removal')
    service_id = fields.Many2one('uni.general.services')
    admission_service_id = fields.Many2one('admission.services')
    student_service_id = fields.Many2one('uni.faculty.student.services')

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        move_id = self.env['account.move'].browse(self._context.get('active_ids', []))
        email = ''
        service_id = False
        student_id = ''
        model_name = ''
        if move_id.payment_state == 'paid':
            if move_id.permission_service_id:
                if move_id.permission_service_id.permission_type == 'travel_permission':
                    move_id.permission_service_id.write({
                        'state':'coordinator',
                        })
                else:
                    if move_id.permission_service_id.service_type_id.require_pickup_delivery:
                        move_id.permission_service_id.write({
                            'execution_start_date':date.today(),
                            'state': 'in_progress'
                            })
                    else:
                        move_id.permission_service_id.write({
                            'state': 'done'
                            })
                service_id = move_id.permission_service_id
                student_id = move_id.permission_service_id.name

            elif move_id.late_registration_service_id:
                move_id.late_registration_service_id.write({
                    'state':'coordinator',
                    })
                service_id = move_id.late_registration_service_id
                student_id = move_id.late_registration_service_id.name

            elif move_id.recorrection_service_id:
                move_id.recorrection_service_id.write({
                    'state':'corrrection_committee',
                    })
                service_id = move_id.recorrection_service_id
                student_id = move_id.recorrection_service_id.student_id

            elif move_id.substitution_service_id:
                move_id.substitution_service_id.write({
                    'state':'program_coordinator',
                    })
                service_id = move_id.substitution_service_id
                student_id = move_id.substitution_service_id.student_id

            elif move_id.fail_removal_service_id:
                move_id.fail_removal_service_id.write({
                    'state':'exam_committee',
                    })
                service_id = move_id.fail_removal_service_id
                student_id = move_id.fail_removal_service_id.student_id

            elif move_id.service_id:
                if move_id.service_id.service_type_id.require_pickup_delivery:
                    move_id.service_id.write({
                        'start_date':date.today(),
                        'state': 'in_progress'
                        })
                else:
                    move_id.service_id.write({
                        'state': 'done'
                        })
                service_id = move_id.service_id
                student_id = move_id.service_id.student_id

            elif move_id.admission_service_id:
                if move_id.admission_service_id.service_type_id.require_pickup_delivery:
                        move_id.admission_service_id.write({
                            'execution_start_date':date.today(),
                            'state': 'in_progress'
                            })
                else:
                    move_id.admission_service_id.write({
                        'state': 'done'
                        })
                service_id = move_id.admission_service_id
                student_id = move_id.admission_service_id.student_id

            elif move_id.student_service_id:
                move_id.student_service_id.write({
                    'state':'program_coordinator',
                    })
                service_id = move_id.student_service_id
                student_id = move_id.student_service_id.student_id

            if service_id:
                if service_id.service_type_id.service_notification and service_id.service_type_id.email_notification:
                    self.send_mail(service_id.service_name,student_id.email,service_id.id,service_id._name)

            return res

    def send_mail(self,mail,sevice,service_id,service_model):
        mail_pool = self.env['mail.mail']

        values={}
        values.update({'subject': sevice})

        values.update({'email_to': mail})

        values.update({'body_html': 'service paid'})

        values.update({'res_id': service_id }) #[optional] here is the record id, where you want to post that email after sending

        values.update({'model': service_model}) #[optional] here is the object(like 'project.project')  to whose record id you want to post that email after sending

        msg_id = mail_pool.create(values)

        # And then call send function of the mail.mail,

        if msg_id:
            print('------------ msg senfd')
            mail_pool.send([msg_id])

