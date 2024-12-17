

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Curriculums(models.Model):
	_inherit = 'uni.faculty.curriculum'

	level_grade = fields.Many2one('grade.conf')
	semester_grade = fields.Many2one('grade.conf')
	subject_grade = fields.Many2one('grade.conf')
	gpa_grade = fields.Many2one('grade.conf')


	def action_approve(self):
		self.curriculum_line_ids.unlink()
		for line in self.curriculum_subjets_line_ids:
			for subject in line.subject_ids:
				component = []
				for degree in subject.degree_component:
					component.append([0,0,{
						'name':degree.name.id,
						'component_type':degree.component_type,
						'percentage':degree.percentage,
						'curriculum_id':self.id,
						}])
				curriculum_line_id = self.curriculum_line_ids.create({
					'level_id':line.level_id.id,
					'semester_id':line.semester_id.id,
					'term_semester_id':line.term_semester_id,
					'subject_id':subject.id,
					'curriculum_id':self.id,
					'subject_type':subject.subject_type,
					'full_degree':subject.full_degree,
					'success_degree':subject.success_degree,
					'subject_grade':subject.subject_grade.id,
					'fail_remove':subject.fail_remove,
					'subject_carry':subject.subject_carry,
					'degree_component':component,
					})
				if subject.subject_type == 'theoretical' or subject.subject_type == 'both':
					curriculum_line_id.theoretical_lectures = subject.theoretical_lectures
					curriculum_line_id.theoretical_credit_hours = subject.theoretical_credit_hours
				if subject.subject_type == 'practical' or subject.subject_type == 'both':
					curriculum_line_id.practical_lectures = subject.practical_lectures
					curriculum_line_id.practical_hours = subject.practical_hours
					curriculum_line_id.practical_credit_hours = subject.practical_credit_hours
		self.state = 'approved'

class Curriculums(models.Model):
	_inherit = 'uni.faculty.curriculum.line'

	full_degree = fields.Float(string="Full Mark")
	degree_component = fields.One2many('subject.degree.component','curriculum_id')
	success_degree = fields.Float(string="Pass Mark")
	subject_grade = fields.Many2one('grade.conf')
	subject_carry = fields.Boolean('Can be carry ?')
	fail_remove = fields.Boolean('Fail can be removed?', default=True)

	# @api.constrains('degree_component','degree_component.percentage','degree_component.exam__id','degree_component.curriculum_id')
	# def check_component(self):
	# 	count = 0
	# 	for component in self.degree_component:
	# 		count += component.percentage
	# 	if count != 100:
	# 		raise ValidationError(_(
	# 			"Sorry, the total percentage of component should be 100 in %s"%self.subject_id.name))



	@api.onchange('subject_id')
	def _get_component(self):
		if self.subject_id:
			self.write({
				'degree_component':[(6,0,self.subject_id.degree_component.ids)]
				}) 


class subjects(models.Model):
	_inherit = 'uni.faculty.subject'

	full_degree = fields.Float(string="Full Mark")
	degree_component = fields.One2many('subject.degree.component','subject_id')
	success_degree = fields.Float(string="Pass Mark")
	subject_grade = fields.Many2one('grade.conf')
	subject_carry = fields.Boolean('Can be carry ?')


class Levels(models.Model):
	_inherit = 'uni.faculty.level'

	level_grade = fields.Many2one('grade.conf')

class Semesters(models.Model):
	_inherit = 'uni.faculty.semester'

	semester_grade = fields.Many2one('grade.conf')

class Component(models.Model):
	_name = 'degree.component'

	name = fields.Char(required=True)
	component_type = fields.Selection(selection=[
		('attendance','Attendance'),
		('year_works','Year Works'),
		('practical','Practical'),
		('final_exam','Final Exam')
	])
	

class Component(models.Model):
	_name = 'subject.degree.component'

	name = fields.Many2one('degree.component',required=True)
	component_type = fields.Selection(related="name.component_type",store=True)
	percentage = fields.Float('Perc(%)',required=True)
	subject_id = fields.Many2one('uni.faculty.subject')
	curriculum_id = fields.Many2one('uni.faculty.curriculum.line')
	exam__id = fields.Many2one('exam.exam')
