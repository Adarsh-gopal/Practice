# -*- coding: utf-8 -*-
{
    'name': "Manufacturing Base",

    'summary': """
        Manufacturing Base""",

    'description': """
        Manufacturing Base
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Manufacturing',
    'version': '13.0.1.1',

    'depends': ['mrp'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/split_mo.xml',
        'views/short_close.xml'
    ],
}
