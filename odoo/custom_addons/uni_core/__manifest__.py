# -*- coding: utf-8 -*-
{
    'name':
    "Madaien uni_core",
    'summary':
    "Faculty Core",
    'description':
    """
        Long description of module's purpose
    """,
    'author':
    "itmayin",
    'website':
    "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category':
    'Uncategorized',
    'version':
    '0.1',

    # any module necessary for this one to work correctly
    'depends': [
    'hr','base_custom', #'account_voucher','stock','purchase','account_budget',
    
    ],

    # always loaded
    'data': [

        'security/uni_core_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',
        'views/views.xml',
        # 'views/faculty_views.xml',
        'views/student_guradian_view.xml',
        'views/student_views.xml',
        'views/program_views.xml',
        'views/level_views.xml',
        'views/semester_views.xml',
        'views/department_views.xml',
        'views/subject_views.xml',
        'views/curriculum_views.xml',
        'views/curriculum_line_views.xml',
        'views/batch_views.xml',
        'views/specialization_views.xml',
        'views/study_calendar_views.xml',
        'views/classrooms_view.xml',
        'views/labs_view.xml',
        'views/faculty_activities_views.xml',
        'views/students_groups_view.xml',
        'report/report_student_preamble.xml',
        'report/header_footer.xml',
        # 'reports/reports_view.xml',
        # 'reports/resignation.xml',
        # 'report/student_card.xml',
        'report/report_menu.xml',
        # 'views/res_company.xml',
        # 'views/fees_payment_line_view.xml',
        # 'views/account_budget_view.xml',
        # 'views/config_setting_view.xml',
    ],
    # only loaded in demonstration mode

    'demo': [
    ],
}
