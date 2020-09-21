{
    'name': 'PO Status Report',
    
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',    
    
    'version': '13.1',
    
    'category': 'Purchase',

    'summary': 'This module is useful to show the purchase order lines with status of GRN and Invoice',

    'description': """This module is useful to show the purchase order lines with status of GRN and Invoice""",
    
    'depends': ['purchase'],
    
    'data': [
        'views/purchase_order_line.xml',
    ],
    
    'auto_install': False,
    'installable' : True,
    'application': True,
}
