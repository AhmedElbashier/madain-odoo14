from odoo import api, fields, models, _
from datetime import date,datetime
from odoo.exceptions import Warning

class StudentReport(models.TransientModel):
    _name = 'letter.report.wizard'
    letter_from= fields.Char(string="From")
    letter_to= fields.Char(string="To")
    student_name= fields.Many2one("uni.admission" ,string=" Student Name")
    # student_name= fields.Char(string="Name")
    letter_date = fields.Date(string= "Date", default=date.today(), readonly=True)
    copy_to= fields.Char(string="Copy To")
    letter_reference=fields.Char(string="Reference")
    admission_manager = fields.Char(string="Admission Manager")
    program = fields.Char(string="Student Program",
                related="student_name.program_id.name" , readonly=True)
    
    def action_print_report(self,data=None):
                      
        data = {
            
            'form_data': self.read()[0],
             }
        
        return self.env.ref('uni_admission.action_letter_report').report_action(self, data=data)

        