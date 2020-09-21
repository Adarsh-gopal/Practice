# -*- coding: utf-8 -*-
{
    'name': "Purchase Base",
    'summary': """
        Base Addon Over Standard Purchase App Odoo 13e""",

    'description': """
        1)Last Purchase Price-------(wiz_last_purchase_price.py/xml,last_purchase_price.xml)
        2)Purchase quote revision------------------------------------(purchase_revision.py/xml)
        3)Purchase order type----------------------------------------(order_type.py/xml)
    """,

    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'company': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "https://www.prixgen.com",

    'category': 'Purchase',
    'version': '13.0.0.2',

    'depends': ['purchase'],

    'data': [
        'security/ir.model.access.csv',
        'views/order_type.xml',
        'wizard/wiz_last_purchase_price.xml',
        'views/last_purchase_price.xml',
        'views/purchase_revision.xml',
    ],
}
