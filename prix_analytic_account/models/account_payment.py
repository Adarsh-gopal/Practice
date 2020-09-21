# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from itertools import groupby
from collections import defaultdict
import pdb

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

	def _prepare_payment_vals(self, invoices):
		'''Create the payment values.

		:param invoices: The invoices/bills to pay. In case of multiple
			documents, they need to be grouped by partner, bank, journal and
			currency.
		:return: The payment values as a dictionary.
		'''
		amount = self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, self.journal_id, self.payment_date)
		values = {
			'journal_id': self.journal_id.id,
			'payment_method_id': self.payment_method_id.id,
			'payment_date': self.payment_date,
			'communication': " ".join(i.invoice_payment_ref or i.ref or i.name for i in invoices),
			'invoice_ids': [(6, 0, invoices.ids)],
			'payment_type': ('inbound' if amount > 0 else 'outbound'),
			'amount': abs(amount),
			'currency_id': invoices[0].currency_id.id,
			'partner_id': invoices[0].commercial_partner_id.id,
			'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
			'partner_bank_account_id': invoices[0].invoice_partner_bank_id.id,
			'z_analytic_account_id': self.z_analytic_account_id.id,
		}
		return values


class account_payment(models.Model):
	_inherit = "account.payment"

	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',help="The analytic account related to a Invoice.")
	z_analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags',copy=True,related="z_analytic_account_id.z_analytic_tag_ids")

	def _prepare_payment_moves(self):
		''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
		to the 'create' method.

		Example 1: outbound with write-off:

		Account             | Debit     | Credit
		---------------------------------------------------------
		BANK                |   900.0   |
		RECEIVABLE          |           |   1000.0
		WRITE-OFF ACCOUNT   |   100.0   |

		Example 2: internal transfer from BANK to CASH:

		Account             | Debit     | Credit
		---------------------------------------------------------
		BANK                |           |   1000.0
		TRANSFER            |   1000.0  |
		CASH                |   1000.0  |
		TRANSFER            |           |   1000.0

		:return: A list of Python dictionary to be passed to env['account.move'].create.
		'''
		all_move_vals = []
		for payment in self:
		    company_currency = payment.company_id.currency_id
		    move_names = payment.move_name.split(payment._get_move_name_transfer_separator()) if payment.move_name else None

		    # Compute amounts.
		    write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
		    if payment.payment_type in ('outbound', 'transfer'):
		        counterpart_amount = payment.amount
		        liquidity_line_account = payment.journal_id.default_debit_account_id
		    else:
		        counterpart_amount = -payment.amount
		        liquidity_line_account = payment.journal_id.default_credit_account_id

		    # Manage currency.
		    if payment.currency_id == company_currency:
		        # Single-currency.
		        balance = counterpart_amount
		        write_off_balance = write_off_amount
		        counterpart_amount = write_off_amount = 0.0
		        currency_id = False
		    else:
		        # Multi-currencies.
		        balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id, payment.payment_date)
		        write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id, payment.payment_date)
		        currency_id = payment.currency_id.id

		    # Manage custom currency on journal for liquidity line.
		    if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
		        # Custom currency on journal.
		        if payment.journal_id.currency_id == company_currency:
		            # Single-currency
		            liquidity_line_currency_id = False
		        else:
		            liquidity_line_currency_id = payment.journal_id.currency_id.id
		        liquidity_amount = company_currency._convert(
		            balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
		    else:
		        # Use the payment currency.
		        liquidity_line_currency_id = currency_id
		        liquidity_amount = counterpart_amount

		    # Compute 'name' to be used in receivable/payable line.
		    rec_pay_line_name = ''
		    if payment.payment_type == 'transfer':
		        rec_pay_line_name = payment.name

		    else:
		        if payment.partner_type == 'customer':
		            if payment.payment_type == 'inbound':
		                rec_pay_line_name += _("Customer Payment")
		            elif payment.payment_type == 'outbound':
		                rec_pay_line_name += _("Customer Credit Note")
		        elif payment.partner_type == 'supplier':
		            if payment.payment_type == 'inbound':
		                rec_pay_line_name += _("Vendor Credit Note")
		            elif payment.payment_type == 'outbound':
		                rec_pay_line_name += _("Vendor Payment")
		        if payment.invoice_ids:
		            rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

		    # Compute 'name' to be used in liquidity line.
		    if payment.payment_type == 'transfer':
		        liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
		    else:
		        liquidity_line_name = payment.name

		    # ==== 'inbound' / 'outbound' ====

		    move_vals = {
		        'date': payment.payment_date,
		        'ref': payment.communication,
		        'journal_id': payment.journal_id.id,
		        'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
		        'partner_id': payment.partner_id.id,
		        'z_analytic_account_id': payment.z_analytic_account_id.id,
		        'line_ids': [
		            # Receivable / Payable / Transfer line.
		            (0, 0, {
		                'name': rec_pay_line_name,
		                'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
		                'currency_id': currency_id,
		                'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
		                'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
		                'date_maturity': payment.payment_date,
		                'partner_id': payment.partner_id.id,
		                'account_id': payment.destination_account_id.id,
		                'payment_id': payment.id,
		            }),
		            # Liquidity line.
		            (0, 0, {
		                'name': liquidity_line_name,
		                'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
		                'currency_id': liquidity_line_currency_id,
		                'debit': balance < 0.0 and -balance or 0.0,
		                'credit': balance > 0.0 and balance or 0.0,
		                'date_maturity': payment.payment_date,
		                'partner_id': payment.partner_id.id,
		                'account_id': liquidity_line_account.id,
		                'payment_id': payment.id,
		            }),
		        ],
		    }
		    if write_off_balance:
		        # Write-off line.
		        move_vals['line_ids'].append((0, 0, {
		            'name': payment.writeoff_label,
		            'amount_currency': -write_off_amount,
		            'currency_id': currency_id,
		            'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
		            'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
		            'date_maturity': payment.payment_date,
		            'partner_id': payment.partner_id.id,
		            'account_id': payment.writeoff_account_id.id,
		            'payment_id': payment.id,
		        }))

		    if move_names:
		        move_vals['name'] = move_names[0]

		    all_move_vals.append(move_vals)

		    # ==== 'transfer' ====
		    if payment.payment_type == 'transfer':
		        journal = payment.destination_journal_id

		        # Manage custom currency on journal for liquidity line.
		        if journal.currency_id and payment.currency_id != journal.currency_id:
		            # Custom currency on journal.
		            liquidity_line_currency_id = journal.currency_id.id
		            transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id, payment.payment_date)
		        else:
		            # Use the payment currency.
		            liquidity_line_currency_id = currency_id
		            transfer_amount = counterpart_amount

		        transfer_move_vals = {
		            'date': payment.payment_date,
		            'ref': payment.communication,
		            'partner_id': payment.partner_id.id,
		            'journal_id': payment.destination_journal_id.id,
		            'z_analytic_account_id': payment.z_analytic_account_id.id,
		            'line_ids': [
		                # Transfer debit line.
		                (0, 0, {
		                    'name': payment.name,
		                    'amount_currency': -counterpart_amount if currency_id else 0.0,
		                    'currency_id': currency_id,
		                    'debit': balance < 0.0 and -balance or 0.0,
		                    'credit': balance > 0.0 and balance or 0.0,
		                    'date_maturity': payment.payment_date,
		                    'partner_id': payment.partner_id.id,
		                    'account_id': payment.company_id.transfer_account_id.id,
		                    'payment_id': payment.id,
		                }),
		                # Liquidity credit line.
		                (0, 0, {
		                    'name': _('Transfer from %s') % payment.journal_id.name,
		                    'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
		                    'currency_id': liquidity_line_currency_id,
		                    'debit': balance > 0.0 and balance or 0.0,
		                    'credit': balance < 0.0 and -balance or 0.0,
		                    'date_maturity': payment.payment_date,
		                    'partner_id': payment.partner_id.id,
		                    'account_id': payment.destination_journal_id.default_credit_account_id.id,
		                    'payment_id': payment.id,
		                }),
		            ],
		        }


		        if move_names and len(move_names) == 2:
		            transfer_move_vals['name'] = move_names[1]


		        all_move_vals.append(transfer_move_vals)
		return all_move_vals



	def _get_move_vals(self, journal=None):
		journal = journal or self.journal_id
		return {
		'date': self.payment_date,
		'ref': self.communication or '',
		'company_id': self.company_id.id,
		'journal_id': journal.id,
		'z_analytic_account_id':self.z_analytic_account_id.id,
        }
	
	def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
		analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
		return {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
            'analytic_tag_ids': analytic_tag_ids,
        }

	def _get_counterpart_move_line_vals(self, invoice=False):
		analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
		if self.payment_type == 'transfer':
			name = self.name
		else:
			name = ''
			if self.partner_type == 'customer':
				if self.payment_type == 'inbound':
					name += _("Customer Payment")
				elif self.payment_type == 'outbound':
					name += _("Customer Credit Note")
			elif self.partner_type == 'supplier':
				if self.payment_type == 'inbound':
					name += _("Vendor Credit Note")
				elif self.payment_type == 'outbound':
					name += _("Vendor Payment")
			if invoice:
				name += ': '
				for inv in invoice:
					if inv.move_id:
						name += inv.number + ', '
				name = name[:len(name)-2]
		return {
            'name': name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'analytic_tag_ids': analytic_tag_ids,
		}