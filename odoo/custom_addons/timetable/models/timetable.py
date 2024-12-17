# -*- coding: utf-8 -*-
import calendar
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

week_days = [(calendar.day_name[0], _(calendar.day_name[0])),
             (calendar.day_name[1], _(calendar.day_name[1])),
             (calendar.day_name[2], _(calendar.day_name[2])),
             (calendar.day_name[3], _(calendar.day_name[3])),
             (calendar.day_name[4], _(calendar.day_name[4])),
             (calendar.day_name[5], _(calendar.day_name[5])),
             (calendar.day_name[6], _(calendar.day_name[6]))]


class OpSession(models.Model):
    _name = "op.session"
    _inherit = ["mail.thread"]
    _description = "Sessions"

    session_type = fields.Selection([('original','Original'),('compensation','Compensation')], default='original')
    name = fields.Char(compute='_compute_name', string='Name', store=True)
    session_number = fields.Integer()
    timing_id = fields.Many2one(
        'op.timing', 'Timing', required=True, tracking=True)
    start_datetime = fields.Datetime(
        'Start Time',
        default=lambda self: fields.Datetime.now())
    end_datetime = fields.Datetime(
        'End Time')
    course_id = fields.Char('Course')
    faculty_id = fields.Many2one(
        'uni.faculty.program', 'Program')
    batch_id = fields.Many2one(
        'uni.faculty.department.batch', 'Batch', required=True)
    subject_id = fields.Many2one(
        'uni.faculty.subject', 'Subject', required=True)
    classroom_id = fields.Many2one(
        'uni.faculty.classroom', 'Classroom')
    calendar_id = fields.Many2one(
        'uni.faculty.calendar', 'Calendar')
    color = fields.Integer('Color Index')
    type = fields.Char(compute='_compute_day', string='Day', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'),
         ('done', 'Done'), ('cancel', 'Canceled')],
        string='Status', default='draft')
    user_ids = fields.Many2many(
        'res.users',
        store=True, string='Users')

    subject_type = fields.Selection([('theoretical','Theoretical'),
        ('practical','Practical'),]
        ,default='theoretical',string='Type')
    subject_groups = fields.Many2one('uni.student.groups',string="Group")
    generation_id = fields.Many2one('generate.time.table')
    program_id = fields.Many2one('uni.faculty.program')
    level_id = fields.Many2one('uni.faculty.level')
    semester_id = fields.Many2one('uni.faculty.semester')
    session_attendees_ids = fields.One2many('op.session.attendees','session_id', copy=True)
    active = fields.Boolean(default=True)
    headline=fields.Text()
    original_lecture = fields.Many2one('op.session')
    compensation_lecture = fields.Many2one('op.session')

    @api.depends('start_datetime')
    def _compute_day(self):
        for record in self:
            if record.start_datetime:
                record.type = fields.Datetime.from_string(
                    record.start_datetime).strftime("%A")

    @api.depends('subject_type', 'subject_id', 'start_datetime', 'subject_groups')
    def _compute_name(self):
        for session in self:
            if session.subject_id:
                session.name = session.subject_id.name + '/' + str(session.session_number) + '/' + session.subject_type
                if session.start_datetime:
                    session.name += '/' + str(session.start_datetime.date()) 
                if session.subject_groups:
                    session.name += '/'+ session.subject_groups.name
    def get_students(self):
        attendees_line =[]
        self.session_attendees_ids = False
        curriculum_line_id = self.env['uni.faculty.curriculum.line'].search([('curriculum_id','=',self.batch_id.curriculum_id.id),('subject_id','=',self.subject_id.id),('level_id','=',self.batch_id.level_id.id),('semester_id','=',self.batch_id.semester_id.id)])
        if self.subject_type == 'theoretical':
            if curriculum_line_id.specialization_id: 
                student_ids = self.env['uni.student'].search([('state','=','student'),('program_id','=',self.batch_id.program_id.id),('batch_id','=',self.batch_id.id),('registration_status','=','registered'),('specialization_id','=',curriculum_line_id.specialization_id.id)])

            else:
                student_ids = self.env['uni.student'].search([('state','=','student'),('program_id','=',self.batch_id.program_id.id),('batch_id','=',self.batch_id.id),('registration_status','=','registered')])
        else:
            student_ids = self.env['uni.student.groups'].search([('academic_year_id','=',self.generation_id.academic_year_id.id),('batch_id','=',self.batch_id.id)],limit=1).student_ids

        attendees_line = self.get_attendees_line(student_ids)
        self.session_attendees_ids = attendees_line

    def get_attendees_line(self,student_ids):
        attendees_line = []
        for student in student_ids:
            attendees_line.append(([0,0,{
                'student_id':student.id,
                'university_id':student.university_id,
                'status':'presence',
                }]))
        return attendees_line

    def reschedule(self): 
        session_id = self.copy(default={'session_type':'compensation','original_lecture':self.id,'start_datetime':False,'end_datetime':False})
        self.compensation_lecture = session_id.id

    def lecture_draft(self):
        self.state = 'draft'

    def lecture_confirm(self):
        self.state = 'confirm'

    def lecture_done(self):
        self.state = 'done'

    def lecture_cancel(self):
        self.state = 'cancel'

    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_time(self):
        if self.start_datetime > self.end_datetime:
            raise ValidationError(_(
                'End Time cannot be set before Start Time.'))

    @api.constrains('faculty_id', 'timing_id', 'start_datetime', 'classroom_id',
                    'batch_id', 'subject_id')
    def check_timetable_fields(self):
        sessions = self.env['op.session'].search([])
        for session in sessions:
            if self.id != session.id:
                if  self.start_datetime and session.start_datetime:
                    if self.classroom_id.id == session.classroom_id.id and \
                        self.timing_id.id == session.timing_id.id and \
                        self.start_datetime.date() == session.start_datetime.date():
                        raise ValidationError(_(
                            'You cannot create a session with same classroom on same date'
                            ' and time'))
                    if self.subject_type == 'theoretical' and self.batch_id.id == session.batch_id.id and \
                            self.timing_id.id == session.timing_id.id and \
                            self.start_datetime.date() == session.start_datetime.date():
                            #and self.subject_id.id == session.subject_id.id:
                        raise ValidationError(_(
                            'You cannot create a session for the same batch on same time '
                            'and for same subject'))
                    # if self.batch_id.id == session.batch_id.id and \
                    #         self.start_datetime.date() == session.start_datetime.date():
                    #     raise ValidationError(_(
                    #         'You cannot create a session for the same batch on same time '
                    #         'even if it is different subject'))
                    # if self.subject_type == 'theoretical' and self.batch_id.id == session.batch_id.id and \
                    #     self.start_datetime.date() == session.start_datetime.date():
                    #     raise ValidationError(_(
                    #         'You cannot create a session for the same subject on same time '))
                    if self.subject_type == session.subject_type and self.batch_id.id == session.batch_id.id and \
                         self.start_datetime.date() == session.start_datetime.date() and \
                         self.timing_id.id == session.timing_id.id and \
                        self.subject_groups == session.subject_groups:
                        raise ValidationError(_(
                            'You cannot create a session for the same group on same time '))


    @api.model
    def create(self, values):
        res = super(OpSession, self).create(values)
        mfids = res.message_follower_ids
        partner_val = []
        partner_ids = []
        for val in mfids:
            partner_val.append(val.partner_id.id)
        # if res.faculty_id and res.faculty_id.user_id:
        #     partner_ids.append(res.faculty_id.user_id.partner_id.id)
        # if res.batch_id and res.course_id:
        #     course_val = self.env['op.student.course'].search([
        #         ('batch_id', '=', res.batch_id.id),
        #         ('course_id', '=', res.course_id.id)
        #     ])
        #     for val in course_val:
        #         if val.student_id.user_id:
        #             partner_ids.append(val.student_id.user_id.partner_id.id)
        subtype_id = self.env['mail.message.subtype'].sudo().search([
            ('name', '=', 'Discussions')])
        if partner_ids and subtype_id:
            mail_followers = self.env['mail.followers'].sudo()
            for partner in list(set(partner_ids)):
                if partner in partner_val:
                    continue
                mail_followers.create({
                    'res_model': res._name,
                    'res_id': res.id,
                    'partner_id': partner,
                    'subtype_ids': [[6, 0, [subtype_id[0].id]]]
                })
        return res

    # def notify_user(self):
    #     for session in self:
    #         template = self.env.ref(
    #             'openeducat_timetable.session_details_changes',
    #             raise_if_not_found=False)
    #         template.send_mail(session.id)

    def get_emails(self, follower_ids):
        email_ids = ''
        for user in follower_ids:
            if email_ids:
                email_ids = email_ids + ',' + str(user.sudo().partner_id.email)
            else:
                email_ids = str(user.sudo().partner_id.email)
        return email_ids

    def get_subject(self):
        return 'Lecture of ' + self.faculty_id.name + \
               ' for ' + self.subject_id.name + ' is ' + self.state

    # def write(self, vals):
    #     data = super(OpSession,
    #                  self.with_context(check_move_validity=False)).write(vals)
    #     for session in self:
    #         if session.state not in ('draft', 'done'):
    #             session.notify_user()
    #     return data

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Sessions'),
            'template': '/openeducat_timetable/static/xls/op_session.xls'
        }]


class SessionAttendees(models.Model):
    _name = "op.session.attendees"
    _inherit = ["mail.thread"]
    _description = "Attendees"


    student_id = fields.Many2one('uni.student')

    university_id = fields.Char(related='student_id.university_id')

    status = fields.Selection(
        [('presence', 'Presence'), ('absence', 'Absence'), ('justified_absence', 'Justified Absence')],
        'Status')

    session_id = fields.Many2one('op.session')