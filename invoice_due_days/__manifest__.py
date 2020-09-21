# See LICENSE file for full copyright and licensing details.
#Changes Made By Prixgen Tech Solutions Pvt Ltd.
{
    'name': 'Invoice Age Days',
    'version': '13.1',
    'category': 'Partner',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'depends': ['base','account',
        'sale_management',
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
