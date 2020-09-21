# -*- coding: utf-8 -*-
{
    'name': "Alternate GL",

    'summary': """
        Alternate GL""",

    'description': """
        Alternate GL
    """,
    
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': "https://www.prixgen.com",
    
    'category': 'Accounting',
    'version': '13.0.1.0',
    
    'depends': ['account','account_accountant'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/alt_gl.xml',
        'views/account_move.xml',
        'views/account_payment.xml'
    ],
}
