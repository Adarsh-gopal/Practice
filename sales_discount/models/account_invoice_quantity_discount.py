# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError



class AccountInvoiceQuantityDiscount(models.Model):
    _name = "account.invoice.quantity.discount"
    _description = "Invoice Discount"
    _order = 'sequence'

    @api.depends('invoice_quantity_discount_id.invoice_line_ids')
    def _compute_base_amount_quantity_discount(self):
        discount_grouped = {}
        for invoice in self.mapped('invoice_quantity_discount_id'):
            discount_grouped[invoice.id] = invoice.get_quantity_discount_values()
        for discount_line in self:
            discount_line.base = 0.0
            if discount_line.discount_id:
                key = discount_line.discount_id.get_grouping_key_quantity_discount({
                    #need to check this group function for a specified class
                    'discount_id': discount_line.discount_id.id,
                    'account_id': discount_line.account_id.id,
                    'account_analytic_id': discount_line.account_analytic_id.id,
                })
                
                
    invoice_quantity_discount_id = fields.Many2one('account.move', string='Invoice Discount', ondelete='cascade', index=True)
    name = fields.Char(string='Discount Description', required=True)
    discount_id = fields.Many2one('sale.discount', string='Discount', ondelete='restrict')
    account_id = fields.Many2one('account.account', string='Discount Account', required=True, domain=[('deprecated', '=', False)])
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic account')
    amount = fields.Monetary()
    amount_rounding = fields.Monetary()
    amount_total = fields.Monetary(string="Amount", compute='_compute_amount_total_quantity_discount')
    manual = fields.Boolean(default=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of invoice discount.")
    company_id = fields.Many2one('res.company', string='Company', related='account_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='invoice_quantity_discount_id.currency_id', store=True, readonly=True)
    base = fields.Monetary(string='Base', compute='_compute_base_amount__quantity_discount', store=True)
    price_discount = fields.Monetary(string='Discount',
        store=True, readonly=True, help="Total amount without taxes")

    @api.depends('amount', 'amount_rounding')
    def _compute_amount_total_quantity_discount(self):
        for tax_line in self:
            tax_line.amount_total = -tax_line.amount + tax_line.amount_rounding

#this module is for storing and displaying the total sum of Quantity discounts in invoice line and to pass to accounts