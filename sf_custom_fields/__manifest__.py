# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SF Dyes Custom fields',
    'version': '13.0.2.18',
    'category': '',
    'summary': 'For all',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'description': """
This module is display the fields .
    """,
    'depends': ['account','base','sale','purchase','mrp','sales_team','mrp','stock'],
    'data': [
        'views/sf_fields_view.xml',
        'security/ir.model.access.csv'
    ],
   
    'installable': True,
    'auto_install': False
}
