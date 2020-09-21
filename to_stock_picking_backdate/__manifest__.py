# -*- coding: utf-8 -*-
{
    'name': "Stock Transfers Backdate",
    'old_technical_name': 'to_stock_picking_validate_manual_time',

    'summary': """
Manual validation date for stock transfers.
        """,

    'description': """
The problem
===========
In Odoo, when you validate a stock transfer, Odoo applies the current time for the transfer date automatically which is sometimes not what you want. For example, you input data for the past.

The solution
============
This module gives the user a chance to input the transfer date manually. During validation of stock transfers,
when the user click on Validate button, a new window will be popped out with a datetime field for your input.
The default value for the field is the current datetime.

The date you input here will also be used for accounting entry's date if the product is configured with automated stock valuation.

Backdate Operations Control
---------------------------

By default, only users in the "Inventory / Manager" group can carry out backdate operations in Inventory application.
Other users must be granted to the access group **Backdate Operations** before she or he can do it.


Known issues
------------

- Since the acounting journal entry's Date field does not contain time, the backdate in accounting may not respect user's timezone,
  and may causes visual discrepancy between stock move's date and accounting date. This is also an issue by Odoo that can be reproduced as below
  
  * assume that your timezone is UTC+7
  * validate a stock transfer at your local time between 00:00 and 07:00
  * go to the corresponding accounting journal entry to find its date could be 1 day earlier than the stock transfer's date 

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

Looking for the one for Odoo 12 or earlier?
===========================================

    """,

    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com', 

    'category': 'Warehouse',
    'version': '0.3',

    'depends': ['stock_account', 'to_backdate'],

    'data': [
        'security/module_security.xml',
        'wizard/stock_picking_backdate_views.xml'
    ],
    'post_init_hook': 'post_init_hook',
    'application': False,
    'installable': True,
    'license': 'OPL-1',
}
