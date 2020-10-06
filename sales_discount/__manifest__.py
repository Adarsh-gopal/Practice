{
    'name': 'Product Discount',
    'version': '13.7',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Sales',
    'summary': 'Discount in sales',
    'description': """ """,
    'depends': ['sale_management','sale','item_product_group','stock','account','report_custom_fields','alternative_uom'],
    'data': [
        'views/account_invoice.xml',
        'views/sale_discount.xml',
        'views/sale_order.xml'
    ],
    'installable': True,
    'auto_install': False,
}
