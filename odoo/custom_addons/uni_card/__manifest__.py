# -*- coding: utf-8 -*-
{
    'name':
    "Student Cards",
    'summary':
    "Faculty Core",
    'description':
    """
        Long description of module's purpose
    """,
    'author':
    "itmayin",
    'website':
    "http://www.itmayin.com",


    'category':
    'Uncategorized',
    'version':
    '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'uni_admission','uni_services',
    ],

    # always loaded
    'data': [

        # 'security/uni_card_security.xml',
        'security/ir.model.access.csv',
        'views/card_views.xml',
        'views/student_view.xml',
        'views/loss_card_service_view.xml',
        'report/student_card.xml',
        'report/report_menu.xml',
    ],
    # only loaded in demonstration mode

    'demo': [
    ],
}
