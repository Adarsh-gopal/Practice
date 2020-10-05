{
    'name': 'Purchase report Template Vahini',
    'version': '13.0.0.1',
    'description': """This module consists, the customized purchase order Templates""",
    'category': 'Localization',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['purchase','l10n_in','web','base',],
    'data': [
	'reports/purchaseorder_report.xml',
        'views/header_footer.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
