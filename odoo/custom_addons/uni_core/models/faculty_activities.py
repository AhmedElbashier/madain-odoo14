from odoo import api, fields, models
from odoo.tools.translate import _


class FacultyActivities(models.Model):
    _name = 'uni.faculty.activities'
    _inherit = ['mail.thread']
    _description = 'Faculty Activities'

    name = fields.Char(string='Name', required=True)

    code = fields.Char(string='Code', readonly=True)

    start_date = fields.Datetime('Start Date', required=True)

    end_date = fields.Datetime('End Date', required=True)

    location = fields.Char('Location', required=True)

    description = fields.Text('Description', required=True)

    advertiser_id = fields.Many2one('res.users', string='Advertiser', default=lambda self: self.env.user)

    target_group = fields.Selection([('employees','Employees'),('students','Students')], required=True)

    employee_group = fields.Selection([('department','Department'),('group','Group'),('all','All Employee')],)

    program_id = fields.Many2one("uni.faculty.program", string="Programs")

    batch_id = fields.Many2one(string="Batch", comodel_name="uni.faculty.department.batch",
     domain="[('program_id','=',program_id)]")

    level_id = fields.Many2one('uni.faculty.level', string='Level')

    semester_id = fields.Many2one('uni.faculty.semester', string="Term")

    activity_type = fields.Selection([('academic','Academic'),('sportive','Sportive')])

    activity_details = fields.Text('Activity Details')

    department_id = fields.Many2one('hr.department', string="Department")

    tag_ids = fields.Many2many('hr.employee.category', string='Group')

    employee_ids = fields.Many2many('hr.employee', compute='compute_partner', store=True)

    student_ids = fields.Many2many('uni.student', compute='compute_partner', store=True)

    # notification_type = fields.Selection([('whatsapp','Whatsapp'),('sms','SMS'),('email','Email')])
    whatsapp_notification=fields.Boolean(string="whatsapp")
    sms_notification=fields.Boolean(string='SMS')
    email_notification=fields.Boolean(string='Email')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    ],default="draft")

    @api.onchange('level_id','program_id')
    def onchange_level_id(self):
        domain = {}
        batch_ids = self.env['uni.faculty.department.batch'].search([('program_id','=',self.program_id.id),('level_id','=',self.level_id.id)]).ids
        domain = {
            'domain':{
                'batch_id':[('id','in',batch_ids)],
                    }
        }
        return domain

    @api.onchange('batch_id')
    def onchange_batch_id(self):
        self.semester_id = self.batch_id.semester_id.id

    @api.depends('target_group','employee_group','department_id','batch_id')
    def compute_partner(self):
        employee_ids =[]
        student_ids = []
        if self.target_group == 'employees':
            if self.employee_group == 'department':
                if self.department_id:
                    employee_ids = self.env['hr.employee'].search([('department_id','=',self.department_id.id)]).ids
            elif self.employee_group == 'all':
                employee_ids = self.env['hr.employee'].search([]).ids
            # elif self.target_group == 'group':
            #     for tag in 
            #     employee_ids = self.env['hr.employee'].search([('')]) 
            if employee_ids:
                self.write({
                    'employee_ids': [(6, 0, employee_ids) ]   
                    }) 
        elif self.target_group == 'students':
            student_ids = self.env['uni.student'].search([('batch_id','=',self.batch_id.id)]).ids
            self.write({
                'student_ids': [(6, 0, student_ids) ]   
                }) 
    def action_approve(self):
        mail_pool = self.env['mail.mail']

        values={}
        if self.target_group == 'employees' and self.employee_ids and self.email_notification:
            for employee in self.employee_ids:

                values.update({'subject': self.name})

                values.update({'email_to': employee.work_email})

                values.update({'body_html': 'Start Date: '+str(self.start_date) + "\n" + 'End Date: '+str(self.end_date) + "\n" + 'Location: '+self.location})

                values.update({'res_id': self.id }) #[optional] here is the record id, where you want to post that email after sending

                values.update({'model': 'uni.faculty.activities' }) #[optional] here is the object(like 'project.project')  to whose record id you want to post that email after sending

                msg_id = mail_pool.create(values)

                # And then call send function of the mail.mail,

                if msg_id:
                    mail_pool.send([msg_id])

        elif self.target_group == 'students' and self.student_ids and self.email_notification:
            for student in self.student_ids:

                values.update({'subject': self.name})

                values.update({'email_to': student.email})

                values.update({'body_html': 'Activity Type: '+self.activity_type + "\n" +'Activity Details: '+self.activity_details + "\n" + 'Start Date: '+str(self.start_date) + "\n" + 'End Date: '+str(self.end_date )+ "\n" + 'Location: '+self.location})

                values.update({'res_id': self.id }) #[optional] here is the record id, where you want to post that email after sending

                values.update({'model': 'uni.faculty.activities' }) #[optional] here is the object(like 'project.project')  to whose record id you want to post that email after sending

                msg_id = mail_pool.create(values)

                # And then call send function of the mail.mail,

                if msg_id:
                    mail_pool.send([msg_id])

        self.state = 'approved'        

    def rest_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, values):
        values['code'] = self.env['ir.sequence'].next_by_code('uni.faculty.activities') or '/'
        return super(FacultyActivities, self).create(values)


class Types(models.Model):
    _name = 'notification.types'

    name = fields.Char()