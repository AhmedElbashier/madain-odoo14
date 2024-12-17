# -*- encoding: utf-8 -*-
from cryptography.fernet import Fernet
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


class OTPWizard(models.TransientModel):
    _name = 'otp.wizard'
    _description = 'OTP Wizard'

    password = fields.Char(required=True)

    resignation_id = fields.Many2one('uni.faculty.student.services')

    suspension_id = fields.Many2one('uni.faculty.student.services')

    general_service_id = fields.Many2one('uni.general.services')

    admission_service_id = fields.Many2one('admission.services')

    late_registration_id = fields.Many2one('uni.late.registration')

    permission_service_id = fields.Many2one('uni.student.permissions')

    substitution_service_id = fields.Many2one('substitution.service')

    fail_removal_service_id = fields.Many2one('fail.removal')

    recorrection_service_id = fields.Many2one('uni.student.recorrection')

    def confirm(self):
        if self.env.context.get('resignation_id'):
            resignation_id = self.env['uni.faculty.student.services'].browse(self.env.context.get('resignation_id'))
            key = bytes(resignation_id.key , 'utf-8')
            password = decrypt(bytes(resignation_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                resignation_id.state='done'

        elif self.env.context.get('suspension_id'):
            suspension_id = self.env['uni.faculty.student.services'].browse(self.env.context.get('suspension_id'))
            key = bytes(suspension_id.key , 'utf-8')
            password = decrypt(bytes(suspension_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                suspension_id.state='done'

        elif self.env.context.get('general_service_id'):
            general_service_id = self.env['uni.general.services'].browse(self.env.context.get('general_service_id'))
            key = bytes(general_service_id.key , 'utf-8')
            password = decrypt(bytes(general_service_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                general_service_id.state='done'

        elif self.env.context.get('admission_service_id'):
            admission_service_id = self.env['admission.services'].browse(self.env.context.get('admission_service_id'))
            key = bytes(admission_service_id.key , 'utf-8')
            password = decrypt(bytes(admission_service_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                admission_service_id.state='done'

        elif self.env.context.get('late_registration_id'):
            late_registration_id = self.env['uni.late.registration'].browse(self.env.context.get('late_registration_id'))
            key = bytes(late_registration_id.key , 'utf-8')
            password = decrypt(bytes(late_registration_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                late_registration_id.state='done'

        elif self.env.context.get('permission_service_id'):
            permission_service_id = self.env['uni.student.permissions'].browse(self.env.context.get('permission_service_id'))
            key = bytes(permission_service_id.key , 'utf-8')
            password = decrypt(bytes(permission_service_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                permission_service_id.state='done'

        elif self.env.context.get('substitution_service_id'):
            substitution_service_id = self.env['substitution.service'].browse(self.env.context.get('substitution_service_id'))
            key = bytes(substitution_service_id.key , 'utf-8')
            password = decrypt(bytes(substitution_service_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                substitution_service_id.state='done'

        elif self.env.context.get('fail_removal_service_id'):
            fail_removal_service_id = self.env['fail.removal'].browse(self.env.context.get('fail_removal_service_id'))
            key = bytes(fail_removal_service_id.key , 'utf-8')
            password = decrypt(bytes(fail_removal_service_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                fail_removal_service_id.state='done'

        elif self.env.context.get('recorrection_service_id'):
            recorrection_service_id = self.env['uni.student.recorrection'].browse(self.env.context.get('recorrection_service_id'))
            key = bytes(recorrection_service_id.key , 'utf-8')
            password = decrypt(bytes(recorrection_service_id.password , 'utf-8'), key).decode()
            if password != self.password:
                raise ValidationError(_('Please Enter The Valid OTP Code.'))
            else:
                recorrection_service_id.state='done'

        
