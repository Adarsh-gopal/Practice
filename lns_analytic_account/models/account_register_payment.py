# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from itertools import groupby
from collections import defaultdict


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}

#on selection of the record in invoice
class payment_register(models.TransientModel):
	_inherit = "account.payment.register"
	
	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',help="The analytic account related to a Invoice.")
	z_analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags',copy=True,related="z_analytic_account_id.z_analytic_tag_ids")