from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class FacultyCalendar(models.Model):
	_name = 'uni.faculty.calendar'
	_inherit = ['mail.thread']
	_description = 'Faculty Calendar'

	name = fields.Char(string='Name', required=True)

	code = fields.Char(string='Code')

	program_ids = fields.Many2many(
		string="Programs",
		comodel_name="uni.faculty.program",
	)

	level_ids = fields.Many2many(
		string="Level",
		comodel_name="uni.faculty.level",
	)

	batch_ids = fields.Many2many(
		'uni.faculty.department.batch',
		string='Batch'
	)

	calendar_activities_ids = fields.One2many(
		comodel_name='uni.faculty.calendar.activities.line',
		inverse_name='faculty_calendar_id',
		)
	
	state = fields.Selection([
		('draft', 'Draft'),
		('approved', 'Approved'),
		('closed', 'Closed'),
	],default="draft")

	@api.constrains('program_ids','level_ids','batch_ids','academic_year_id')
	def _check_calender(self):
		calender_id = False
		if self.batch_ids:
			calender_id = self.search([('academic_year_id','=',self.academic_year_id.id),('batch_ids','in',self.batch_ids.ids),('id','!=',self.id)])
			if calender_id:
				raise ValidationError(_("You can not create two calender for the same batch"))

		else:
			if self.program_ids and not self.level_ids:
				calender_id = self.search([('academic_year_id','=',self.academic_year_id.id),('program_ids','in',self.program_ids.ids),('level_ids','=',False),('batch_ids','=',False),('id','!=',self.id)])
				if calender_id:
					raise ValidationError(_("You can not create two calender for the same program with same details (%s" % calender_id.name+")"))

			elif self.program_ids and self.level_ids:
				calender_id = self.search([('academic_year_id','=',self.academic_year_id.id),('program_ids','in',self.program_ids.ids),('level_ids','in',self.level_ids.ids),('batch_ids','=',False),('id','!=',self.id)])
				if calender_id:
					raise ValidationError(_("You can not create two calender for the same program in the same level (%s" % calender_id.name+")"))

			elif not self.program_ids and not self.level_ids :
				calender_id = self.search([('academic_year_id','=',self.academic_year_id.id),('program_ids','=',False),('level_ids','=',False),('batch_ids','=',False),('id','!=',self.id)])
				if calender_id:
					raise ValidationError(_("You can not create two calender with same details (%s" % calender_id.name+")"))

			elif self.level_ids and not self.program_ids:
				calender_id = self.search([('academic_year_id','=',self.academic_year_id.id),('program_ids','=',False),('level_ids','in',self.level_ids.ids),('batch_ids','=',False),('id','!=',self.id)])
				if calender_id:
					raise ValidationError(_("You can not create two calender for the same level (%s" % calender_id.name+")"))


	@api.onchange('program_ids','level_ids')
	def onchange_program_id(self):
		domain = {}
		if self.program_ids and self.level_ids:
			domain = {
				'domain':{
				'batch_ids':[('program_id','in',self.program_ids.ids),('level_id','in',self.level_ids.ids)],
				}
			}
		elif self.program_ids and not self.level_ids:

			domain = {
				'domain':{
				'batch_ids':[('program_id','in',self.program_ids.ids)],
				}
			}
		elif self.level_ids and not self.program_ids:

			domain = {
				'domain':{
				'batch_ids':[('level_id','in',self.level_ids.ids)],
				}
			}
	   
		return domain

	def action_approve(self):
		self.state = 'approved'

	def action_close(self):
		self.state = 'closed'

	def rest_draft(self):
		self.state = 'draft'

class FacultyCalendarActivitiesLine(models.Model):
	_name = 'uni.faculty.calendar.activities.line'
	_order = 'start_date'

	sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)

	name = fields.Many2one('uni.calendar.activities', string='Name', required=True)

	start_date = fields.Date('Start Date', required=True)

	end_date = fields.Date('End Date', required=True)

	days_number = fields.Integer('Days')

	week_number = fields.Integer('Weeks')

	faculty_calendar_id = fields.Many2one('uni.faculty.calendar')

	@api.constrains('start_date', 'end_date')
	def check_dates(self):
		start_date = fields.Date.from_string(self.start_date)
		end_date = fields.Date.from_string(self.end_date)
		if start_date < self.faculty_calendar_id.academic_year_id.start_date or start_date > self.faculty_calendar_id.academic_year_id.end_date:
			raise ValidationError(_("Start date must be between academic year start and end date."))
		if end_date < self.faculty_calendar_id.academic_year_id.start_date or end_date > self.faculty_calendar_id.academic_year_id.end_date:
			raise ValidationError(_("End date must be between academic year start and end date."))
		if start_date > end_date:
			raise ValidationError(_("End Date cannot be set before Start Date."))

	@api.constrains('name')
	def check_name(self):
		for rec in self:
			active_line_id = self.env['uni.faculty.calendar.activities.line'].search([('faculty_calendar_id','=',rec.faculty_calendar_id.id),('name','=',rec.name.id),('id','!=',rec.id)],limit=1)
			if active_line_id:
				raise ValidationError(_("The activity %s" % rec.name.name+" is already added"))


	@api.onchange('start_date','end_date')
	def get_days_weeks(self):
		if self.start_date and self.end_date:
			days = (self.end_date - self.start_date).days + 1
			week_days = (self.end_date - self.start_date).days + 1
			if week_days > 6:
				counter = 0
				while week_days > 6:
					counter += 1
					week_days -= 7
				self.week_number = counter
			else:
				self.week_number = 0
			self.days_number = days



class CalendarActivities(models.Model):
	_name = 'uni.calendar.activities'
	_inherit = ['mail.thread']

	name = fields.Char(string='Name', required=True)

	activity_type = fields.Selection([
		('first_sem','First semester study'),
		('second_sem','Second semester study'),
		('first_sem_exam','First semester exams'),
		('sec_sem_exam','Second semester exams'),
		('first_sem_sub_exam','First semester substitutionals exams'),
		('sec_sem_sub_exam','Second semester substitutionals exams'),
		('first_sem_supp_exam','First semester supplement exams'),
		('sec_sem_supp_exam','Second semester supplement exams'),
		],string='Type')

	code = fields.Char(string='Code', readonly=True)

	student_activity = fields.Boolean('Student Activity')

	@api.model
	def create(self, values):
		values['code'] = self.env['ir.sequence'].next_by_code('uni.calendar.activities') or '/'
		return super(CalendarActivities, self).create(values)