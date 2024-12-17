# -*- coding: utf-8 -*-
##############################################################################
#
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Faculty Services",
    'summary': """
    """,
    'description': """
    """,
    'author': 'itmayin',
    'website': 'http://www.yourcompany.edu',
    'version': '0.0.1',
    'depends': ['uni_admission'],
    'data': [
        'security/ir.model.access.csv',
        'data/service_request_seq.xml',
        'views/views.xml',
        'views/res_config_view.xml',
        'wizard/otp_wizard_views.xml',
        'wizard/confirmation_wizard_views.xml',
        'views/faculty_service_type_view.xml',
        'views/faculty_services_view.xml',
        'views/permissions_views.xml',
        'views/student_services_view.xml',
        'views/recorrection_service_view.xml',
        'views/study_schedules_views.xml',
        'views/entry_permission_view.xml',
        'views/substitution_service_view.xml',
        'views/late_registration_views.xml',
        'views/fail_removal_view.xml',
        'views/admission_services_view.xml',
        'reports/reports_view.xml',
        'reports/resignation.xml',
        'reports/substitution.xml',
        'views/exam_types_view.xml',
        'reports/recorrection_form_template.xml',
        'reports/fail_removal_form_template.xml',
        'reports/reports_view.xml',

    ],
    'demo': [],
}
