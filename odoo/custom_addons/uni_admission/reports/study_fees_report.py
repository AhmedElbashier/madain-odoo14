

from odoo import models, fields, api

class StudyFees(models.AbstractModel):
    _name = 'report.uni_admission.report_study_fees_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        # fees_id = data['form']['']
        print('+++++++++++++++ data',data)

        # reg_fees = self.env['uni.registered.fees'].search([
        #     ('uni_study_fees_id','=',)])

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            # 'docs': docs,
        }


