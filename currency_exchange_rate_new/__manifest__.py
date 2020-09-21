# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Currency Exchange',
    'version': '13.15',
    'category': 'Accounting',
    'summary': 'change the currency rates new',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'description': """
This module will change the currency rates . and 
Currency Inverse Rate
==========================
In some countries where currency rate is big enough compared to USD or EUR, 
we are used to see exchange rate in the inverse way as Odoo shows it. 

The module shows rate FROM base currency and not TO base currency. For eg.

* Base Currency IDR: 1.0
* USD rate: 12,000 (in Odoo way: 1 / 12,000 = 0.000083333333333)

Using this module, we enter the 12,000 and not the 0.000083333333333.

This module also add number of decimal precision on the currency rate
to avoid rounding for those currencies.

    """,
    'depends': [ 'account','stock'],
    'data': [
        'views/currency_rate_views.xml',
    ],
   
    'installable': True,
    'auto_install': False
}
