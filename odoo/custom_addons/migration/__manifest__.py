# -*- coding: utf-8 -*-
##############################################################################
#
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Migration",
    'summary': """
    """,
    'description': """
    """,
    'author': 'itmayin',
    'website': 'http://www.yourcompany.edu',
    'version': '0.0.1',
    'depends': ['uni_admission','uni_core','uni_services','uni_results','web_domain_field'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/migration_views.xml',
       
    ],
    'demo': [],
}
