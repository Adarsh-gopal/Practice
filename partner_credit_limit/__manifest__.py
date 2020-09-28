# See LICENSE file for full copyright and licensing details.
#Changes Made By Prixgen Tech Solutions Pvt Ltd.
{
    'name': 'SF Dyes Partner Credit Limit',
    'version': '13.0.1.9',
    'category': 'Partner',
    'license': 'AGPL-3',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['base','sale',
        'sale_management','dev_sale_order_double_approval','account',
    ],
    'data': [
        'views/partner_view.xml',
        'wizard/info.xml',
    ],
    'installable': True,
    'auto_install': False,
}
