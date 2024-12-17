# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class FulFillmentSubject(models.Model):
    _name = 'uni.admission.fulfillment.subject'
    _description = 'FulFillment Subject'
    _inherit = ['mail.thread']

    subject_id = fields.Many2one('uni.faculty.subject', string='Subject', required=True)

    level_id = fields.Many2one('uni.faculty.level', required=True)

    semester_id = fields.Many2one('uni.faculty.semester', string='Term', required=True)

    academic_year_id = fields.Many2one('uni.year', required=True)

    batch_id = fields.Many2one('uni.faculty.department.batch', domain="[('program_id','=',program_id)]", required=True)

    program_id = fields.Many2one('uni.faculty.program', related='admission_id.program_id')

    admission_batch_id= fields.Many2one('uni.faculty.department.batch', related='admission_id.batch_id')

    admission_id = fields.Many2one('uni.admission')

    student_id = fields.Many2one('uni.student',related="admission_id.student_id",store=True)


    @api.onchange('program_id','batch_id','level_id','semester_id')
    def onchange_program_id(self):
        domain = {}
        subjects = []
        curriculum_subjects_line_id = self.env['curriculum.subjects.line']
        self.subject_id = False
        ''' Subject Domain '''
        curriculum_id = self.env['uni.faculty.curriculum'].search([('program_id','=',self.program_id.id),('batch_id','=',self.batch_id.id)],limit=1)
        if curriculum_id:
            curriculum_subjects_line_id = self.env['curriculum.subjects.line'].search([('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('program_id','=',self.program_id.id),('curriculum_id','=',curriculum_id.id)],limit=1)
        else:
            curriculum_subjects_line_id = self.env['curriculum.subjects.line'].search([('level_id','=',self.level_id.id),('semester_id','=',self.semester_id.id),('program_id','=',self.program_id.id)],limit=1)

        subjects = curriculum_subjects_line_id.subject_ids.ids
        
        ''' Group Domain '''
        

        domain = {
            'domain':{
            'subject_id':[('id','in',subjects)],
            }
        }
       
        return domain
