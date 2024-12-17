
from odoo import api, fields, models, _


class Guradians(models.Model):
    _name = 'uni.student.guradian'

    name = fields.Char(string='Name', required=True)
    relation_id = fields.Many2one('uni.family.relation')
    phone = fields.Char()
    contact_ids = fields.One2many('guradian.contact','guradian_id')
    email = fields.Char()
    student_id = fields.Many2one('uni.student')

class GuradiansContact(models.Model):
    _name = 'guradian.contact'

    phone = fields.Char(required=True)
    whatsapp_number = fields.Boolean()
    guradian_id = fields.Many2one('uni.student.guradian')
    student_id = fields.Many2one('uni.student')


class FamilyRelations(models.Model):
    _name = 'uni.family.relation'


    name = fields.Char(required=True)