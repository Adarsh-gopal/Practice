{
    'name': 'SF Sales Quotation',
    'version': '13.0.0.10',
    'description': """This module consists, the customized quotation report""",
    'category': 'Localization',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['sale','l10n_in','web','base',],
    'data': [

        'reports/quotation_report.xml',
        'reports/pro_forma.xml',
        'templates/header_footer.xml',
        'templates/destination.xml',
        
    ],
    'installable': True,
    'application': False,
}
