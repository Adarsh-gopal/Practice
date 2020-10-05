# -*- coding: utf-8 -*-
{
    'name': "Quality Control Base",

    'summary': """
        Quality Base""",

    'description': """
        Quality Base
    """,

    'author': "Prixgen Tech Solutions Pvt Ltd",
    'website': "http://www.prixgen.com",

    
    'category': 'Quality',
    'version': '13.0.3.1',

    
    'depends': ['base','stock','product','quality','quality_control','mrp','quality_mrp'],

    
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
