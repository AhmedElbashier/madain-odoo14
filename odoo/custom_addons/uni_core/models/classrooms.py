
from odoo import api, fields, models



class Classroom(models.Model):
    _name = 'uni.faculty.classroom'
    _inherit = ['mail.thread']

    name = fields.Char()
    code = fields.Char()
    class_type = fields.Selection(selection=[
        ('classroom','Classroom'),
        ('lab','Lab')
    ])
    building_id = fields.Many2one('uni.faculty.building')
    capacity = fields.Integer()
    teaching_adis_ids = fields.Many2many('uni.faculty.teaching.adis', string="Teaching Tools")
    asset_ids = fields.Many2many('uni.faculty.assets',string="Assets")

    # @api.model
    # def create(self, vals):
    #     if vals['class_type'] == 'classroom':
    #         vals['code'] = self.env['ir.sequence'].next_by_code('classroom') or '/'
    #     if vals['class_type'] == 'lab':
    #         vals['code'] = self.env['ir.sequence'].next_by_code('lab') or '/'
    #     res = super(Classroom, self).create(vals)
    #     return res


class Building(models.Model):
    _name = 'uni.faculty.building'
    _inherit = ['mail.thread']

    name = fields.Char()
    code = fields.Char()

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].next_by_code('building') or '/'
    #     res = super(Building, self).create(vals)
    #     return res


class TeachingAdis(models.Model):
    _name = 'uni.faculty.teaching.adis'
    _inherit = ['mail.thread']

    name = fields.Char()
    code = fields.Char()

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].next_by_code('teaching.adis') or '/'
    #     res = super(TeachingAdis, self).create(vals)
    #     return res


class Assets(models.Model):
    _name = 'uni.faculty.assets'
    _inherit = ['mail.thread']

    name = fields.Char()
    code = fields.Char()

    # @api.model
    # def create(self, vals):
    #     vals['code'] = self.env['ir.sequence'].next_by_code('assets') or '/'
    #     res = super(Assets, self).create(vals)
    #     return res