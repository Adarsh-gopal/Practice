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
class SaleDiscount(models.Model):
    _name = "sale.discount"

    name = fields.Char(string="Discount Name")
    discount_type = fields.Selection([('quantity', 'Quantity Discount'),('special', 'Special Discount'),('trade','Trade Discount')],string="Discount Type")
    account_id = fields.Many2one('account.account', string='Account Debit', required=True, domain=[('deprecated', '=', False)])
    refund_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Account Credit', ondelete='restrict')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    include_base_amount = fields.Boolean(string='Affect Base of Subsequent Taxes', default=False,
        help="If set, taxes which are computed after this one will be computed based on the price tax included.")
    sequence = fields.Integer(required=True, default=1,
        help="The sequence field is used to define order in which the tax lines are applied.")
    analytic = fields.Boolean(string="Include in Analytic Cost", help="If set, the amount computed by this tax will be assigned to the same analytic account as the invoice line (if any)")

    def get_grouping_key_trade_discount(self, invoice_discount_vals):
        for l in self:
            return str(invoice_discount_vals['discount_id']) + '-' + str(invoice_discount_vals['account_id'])



    def compute_all_trade_discount(self, price_unit,trade, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        discount = []
        base = 0
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the tax and the total
        # amounts. For example, in SO/PO line, we don't want to round the price unit at the
        # precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5


        # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
        # search. However, the search method is overridden in account.tax in order to add a domain
        # depending on the context. This domain might filter out some taxes from self, e.g. in the
        # case of group taxes.
        for dis in self.sorted(key=lambda r: r.sequence):
           
            '''if dis.amount_type == 'group':
                children = dis.children_discount_ids.with_context(base_values=(base))
                ret = children.compute_all(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['base'] if dis.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue'''

            discount_amount = dis._compute_amount_trade_discount(price_unit,trade, quantity, product, partner)
            if not round_tax:
                discount_amount = round(discount_amount, prec)
            else:
                discount_amount = currency.round(discount_amount)

            # Keep base amount used for the current tax
            
            discount_base = 10


            discount.append({
                'id': dis.id,
                'name': dis.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': discount_amount,
                'sequence': dis.sequence,
                'account_id': dis.account_id.id,
                'refund_account_id': dis.refund_account_id.id,
                'analytic': dis.analytic,

            })

        return {
            'discount': sorted(discount, key=lambda k: k['sequence']),
        }

    def _compute_amount_trade_discount(self, price_unit, trade,quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()
        self.trade_amount=trade
        return self.trade_amount
#quantity


    def get_grouping_key_quantity_discount(self, invoice_discount_vals):
        for l in self:
            return str(invoice_discount_vals['discount_id']) + '-' + str(invoice_discount_vals['account_id'])


    
    def compute_all_quantity_discount(self, price_unit,qty, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        discount = []
        base = 0
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the tax and the total
        # amounts. For example, in SO/PO line, we don't want to round the price unit at the
        # precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5


        # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
        # search. However, the search method is overridden in account.tax in order to add a domain
        # depending on the context. This domain might filter out some taxes from self, e.g. in the
        # case of group taxes.
        for dis in self.sorted(key=lambda r: r.sequence):
           
            '''if dis.amount_type == 'group':
                children = dis.children_discount_ids.with_context(base_values=(base))
                ret = children.compute_all(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['base'] if dis.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue'''

            discount_amount = dis._compute_amount_quantity_discount(price_unit,qty, quantity, product, partner)
            if not round_tax:
                discount_amount = round(discount_amount, prec)
            else:
                discount_amount = currency.round(discount_amount)

            # Keep base amount used for the current tax
            
            discount_base = 10


            discount.append({
                'id': dis.id,
                'name': dis.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': discount_amount,
                'sequence': dis.sequence,
                'account_id': dis.account_id.id,
                'refund_account_id': dis.refund_account_id.id,
                'analytic': dis.analytic,

            })

        return {
            'discount': sorted(discount, key=lambda k: k['sequence']),
        }

    def _compute_amount_quantity_discount(self, price_unit, qty,quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()
        self.quantity_amount=qty
        return self.quantity_amount

#special
    def get_grouping_key_special_discount(self, invoice_discount_vals):
        for l in self:
            return str(invoice_discount_vals['discount_id']) + '-' + str(invoice_discount_vals['account_id'])


    
    def compute_all_special_discount(self, price_unit,special, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        discount = []
        base = 0
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the tax and the total
        # amounts. For example, in SO/PO line, we don't want to round the price unit at the
        # precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5


        # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
        # search. However, the search method is overridden in account.tax in order to add a domain
        # depending on the context. This domain might filter out some taxes from self, e.g. in the
        # case of group taxes.
        for dis in self.sorted(key=lambda r: r.sequence):
           
            '''if dis.amount_type == 'group':
                children = dis.children_discount_ids.with_context(base_values=(base))
                ret = children.compute_all(price_unit, currency, special, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['base'] if dis.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue'''

            discount_amount = dis._compute_amount_special_discount(price_unit,special, quantity, product, partner)
            if not round_tax:
                discount_amount = round(discount_amount, prec)
            else:
                discount_amount = currency.round(discount_amount)

            # Keep base amount used for the current tax
            
            discount_base = 10


            discount.append({
                'id': dis.id,
                'name': dis.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': discount_amount,
                'sequence': dis.sequence,
                'account_id': dis.account_id.id,
                'refund_account_id': dis.refund_account_id.id,
                'analytic': dis.analytic,

            })

        return {
            'discount': sorted(discount, key=lambda k: k['sequence']),
        }

    def _compute_amount_special_discount(self, price_unit, special,quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * special eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()
        self.special_amount=special
        return self.special_amount
