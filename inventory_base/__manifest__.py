# -*- coding: utf-8 -*-
{
    'name': "inventory_base_1.0",

    'summary': """
        Base Customization On Inventory(stock)""",

    'description': """
        Included Functionalities -
            1) Disallow negative inventory in the product master.-----------------------------(disallow_negative_inv.py/xml)
            2) Product Category Filtered based on 'release' Boolean and Description Field.----(categ_release_and_desc.py/xml)
            3) Product/Item Groups.----------------------------------------------------------------(product_groups.py/.xml)
            4) Update Quantity Button Invisible and 'quantity on hand' readonly.--------------(update_qty.xml)
            5) Product Category Dropdown No Create Edit.--------------------------------------(product_categ_no_create_edit.xml)
            6) Product Internal Reference Sequence Based on Category.-------------------------(prod_internal_ref_on_categ.py/xml)
            7) Product Category, Cost in Log note and Category change authorization-----------(product_cost_categ_track.py, product_categ_change_access.xml)
    """,

    'author': "Prixgen Tech Solutions Pvt Ltd",
    'website': "http://www.yourcompany.com",

    'category': 'Customization',
    'version': '13.0.1.0',

    'depends': ['base','stock','product'],

    'data': [
        'security/ir.model.access.csv',
        'security/product_categ_change_access.xml',
        'views/update_qty.xml',
        'views/product_groups.xml',
        'views/disallow_negative_inv.xml',
        'views/categ_release_and_desc.xml',
        'views/product_categ_no_create_edit.xml',
        'views/prod_internal_ref_on_categ.xml',
    ],
}