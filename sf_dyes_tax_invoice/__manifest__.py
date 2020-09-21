{
    'name': 'SF Tax Invoice',
    'version': '13.0.0.16',
    'description': """This module consists, the customized tax invoice""",
    'category': 'Localization',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['account','l10n_in','web','base','product'],
    'data': [
        'reports/invoice_report.xml',
        'templates/header_footer.xml',
    ],
    'installable': True,
    'application': False,
}
