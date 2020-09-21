# -*- coding: utf-8 -*-
{
    'name': 'Manufacture Log Sheet',
    'version': '13.0.0.2',
    'description': """This module consists, the customized Manufacture Log Sheet report""",
    'category': 'Localization',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['base','mrp','web'],
    'data': [
        'views/header_footer.xml',
        'report/manufacture_log_report.xml',
    ],
    'installable': True,
    'application': False,
}
