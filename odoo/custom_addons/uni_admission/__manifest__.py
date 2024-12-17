# -*- coding: utf-8 -*-
{
    'name': "uni_admission",
    'summary':
    """
		Short (1 phrase/line) summary of the module's purpose, used as
		subtitle on modules listing or apps.openerp.com""",
    'description':
    """
		Long description of module's purpose
	""",

        'author': "itmayin",
        'website': "http://www.yourcompany.com",

        # Categories can be used to filter modules in modules listing
        # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
        # for the full list
        'category': 'Uncategorized',
        'version': '0.1',
        # any module necessary for this one to work correctly
        'depends': ['uni_core', 'website','account'],#'uofk_payment'

        # always loaded
        'data': [
            'security/uni_admission_security.xml',
            'security/ir.model.access.csv',
            'data/sequence.xml',
            'views/views.xml',
            'views/registration_views.xml',
            'views/res_company_view.xml',
            'views/account_views.xml',
            'views/post_payment_view.xml',
            # 'views/templates.xml',
            'views/templates_view.xml',
            'views/student_migration_views.xml',
            'wizard/student_migration_wizard_views.xml',
            'views/admission_views.xml',
            'views/student_views.xml',
            'views/nationality_type_views.xml',
            'views/identity_type_views.xml',
            'views/tuition_fees_views.xml',
            # 'views/category_views.xml',
            'views/year_views.xml',
            'views/student_fees.xml',
            'views/batch_views.xml',
            'views/fees_installment_view.xml',
            'views/study_calendar_views.xml',
            'views/discount_scholarship.xml',
            'views/discount_scholarship_request.xml',
            'views/student_guradian_view.xml',
            'views/student_groups_view.xml',
            # 'report/report.xml',
            # 'report/payment_report.xml.xml',
            # 'report/student_statment.xml',

            #'report/admission_analytic_report.xml',
            #'views/account_config_settings_view.xml',
            #'report/report.xml',
            #'wizard/general_report_wizard_view.xml',
            #'wizard/registration_statistics_wizard_view.xml',
            #'report/general_report.xml',
            #'report/registration_statistics_report.xml',
            #'report/tution_fees_report.xml',
            #'wizard/admission_statistical.xml',
            #'report/admission_statistical_report.xml',
            #'wizard/admission_statistical_detailed.xml',
            #'report/admission_statistical_detailed_report.xml',
            #'wizard/collage_share_wizard_view.xml',
            #'report/collage_share_report.xml',
            'wizard/admission_confirm_wizard_views.xml',
            'wizard/letter_report_wizard.xml',
            
            'reports/admission_form_template.xml',
            'reports/receipt_permission_template.xml',
            'reports/study_fees_template.xml',
            'reports/guides_and_steps_template.xml',
            'reports/letter_report.xml',
            'reports/initial_acceptance_template.xml',
            'reports/registeration_form_template.xml',
            'reports/reports_view.xml',
            'reports/header_footer.xml',
            
        ],
    # only loaded in demonstration mode
    'demo': [],
}
