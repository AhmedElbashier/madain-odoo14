
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Recorrection(models.Model):
	_inherit = 'recorrection.subject'


	@api.constrains('academic_year_id','level_id','semester_id','exam_type_ids')
	def check_recorrection_period(self):
		result_record_id = self.env['uni.result.record'].search([('state','=','recorrection_period'),('exam_type_id','=',self.exam_type_ids.id),('year_id','=',self.academic_year_id.id),('batch_id','=',self.batch_id.id)])
		if not result_record_id:
			raise ValidationError(_("There is no open recorrection period for this student."))