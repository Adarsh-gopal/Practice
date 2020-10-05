# -*- coding: utf-8 -*-

{
    'name': "Operator Login",
    'version': '13.1',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'summary': "Operator Login.",
    'description': """  """,
    'depends': ['base','mrp','man_power','resource','hr'],
    'data': [

        'views/mrp_production.xml',
        'views/mrp_workorder.xml',
        'views/operator_login.xml',
        'views/split_manufacturing.xml',
        
        
    ],
'images': ['static/description/icon.png'],
        'installable': True,
    'auto_install': False,
}
