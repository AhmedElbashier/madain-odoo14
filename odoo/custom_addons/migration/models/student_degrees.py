from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StudentDegrees(models.Model):
    _name = "student.degrees"
    _description = "Student Degrees"

    code = fields.Char('Code', required=True)
    student_id = fields.Many2one('uni.student')
    university_id = fields.Char(string="University ID")
    sub1 = fields.Float(string= "Subject(1)") 
    sub2 = fields.Float(string= "Subject(2)") 
    sub3 = fields.Float(string= "Subject(3)") 
    sub4 = fields.Float(string= "Subject(4)") 
    sub5 = fields.Float(string= "Subject(5)") 
    sub6 = fields.Float(string= "Subject(6)") 
    sub7 = fields.Float(string= "Subject(7)") 
    sub8 = fields.Float(string= "Subject(8)") 
    sub9 = fields.Float(string= "Subject(9)") 
    sub10 = fields.Float(string= "Subject(10)") 
    active = fields.Boolean(string="Active", default=True)


    @api.model
    def create(self, values):
        student_id = self.env['uni.student'].search([('university_id','=',values['university_id'])])
        values['student_id'] = student_id.id
        return super(StudentDegrees, self).create(values)



    