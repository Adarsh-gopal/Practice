# -*- coding: utf-8 -*-
{
    'name': "Sale Base",
    'version': '13.0.0.1',
    'summary': """
        Base Addon Over Standard Sale App Odoo 13e""",

    'description': """
        1)Seperate sequences for Sale Quotations and Orders-------(quotation_sequence.py/xml)
        2)Sales quote revision------------------------------------(sale_revision_history.py/xml)
        3)Sales order type----------------------------------------(order_type.py/xml)
    """,

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',

    'category': 'Sale',
    
    'depends': ['sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'views/order_type.xml',
        'views/quotation_sequence.xml',
        'views/sale_revision_history.xml',
        'data/ir_sequence_data.xml',
    ],
}
