# -*- coding: utf-8 -*-

import json
import re
import uuid
from functools import partial

from lxml import etree
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging
import pdb

_
_logger = logging.getLogger(__name__)

#forbidden fields
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')


MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountMove(models.Model):
	_inherit = "account.move"


	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
	z_sourec= fields.Char('Source Ref')


	
	'''@api.model
	def _get_refund_modify_read_fields(self):
		read_fields = ['type','z_analytic_account_id', 'number', 'invoice_line_ids', 'tax_line_ids',
                       'date']
		return self._get_refund_common_fields() + self._get_refund_prepare_fields() + read_fields'''

	
	def action_invoice_open(self):
		# lots of duplicate calls to action_invoice_open, so we remove those already open
		to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
		if to_open_invoices.filtered(lambda inv: not inv.z_analytic_account_id):
			raise UserError(_('Kindly select the Analytic Account before Validating this Invoice'))
		'''if to_open_invoices.filtered(lambda inv: not inv.partner_id):
									raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
								if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
									raise UserError(_("Invoice must be in draft state in order to validate it."))
								if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
									raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
								if to_open_invoices.filtered(lambda inv: not inv.account_id):
									raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
								to_open_invoices.action_date_assign()
								to_open_invoices.action_move_create()
								return to_open_invoices.invoice_validate()'''
		return super(AccountInvoice, self).action_invoice_open()

	
	@api.onchange('z_analytic_account_id')
	def onchange_product_id_analytic_tags(self):
		for lines in self:
			# pdb.set_trace()
			if lines.type != "out_invoice":
				for line in lines.invoice_line_ids:
					rec = self.env['account.analytic.account'].search([('id', '=', lines.z_analytic_account_id.id)])
					line.analytic_tag_ids = False
					line.analytic_tag_ids = rec.z_analytic_tag_ids.ids

	@api.onchange('invoice_origin')
	def onchange_journal(self):
		for l in self:
			if l.invoice_origin:
				sale_order_id =self.env['sale.order'].search([('name','=',l.invoice_origin)])
				if sale_order_id:
					l.journal_id = sale_order_id.l10n_in_journal_id.id



	



	# Overinding the onchnage function for get the Analyatic account
	@api.onchange('purchase_vendor_bill_id', 'purchase_id')
	def _onchange_purchase_auto_complete(self):
		''' Load from either an old purchase order, either an old vendor bill.

		When setting a 'purchase.bill.union' in 'purchase_vendor_bill_id':
		* If it's a vendor bill, 'invoice_vendor_bill_id' is set and the loading is done by '_onchange_invoice_vendor_bill'.
		* If it's a purchase order, 'purchase_id' is set and this method will load lines.

		/!\ All this not-stored fields must be empty at the end of this function.
		'''
		# pdb.set_trace()
		if self.purchase_vendor_bill_id.vendor_bill_id:
		    self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
		    self._onchange_invoice_vendor_bill()
		elif self.purchase_vendor_bill_id.purchase_order_id:
		    self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
		self.purchase_vendor_bill_id = False

		if not self.purchase_id:
		    return

		# Copy partner.
		self.partner_id = self.purchase_id.partner_id
		self.fiscal_position_id = self.purchase_id.fiscal_position_id
		self.invoice_payment_term_id = self.purchase_id.payment_term_id
		self.currency_id = self.purchase_id.currency_id
		#  Fteching the analytic account from po to VB
		if self.purchase_id:
			self.z_analytic_account_id = self.purchase_id.z_account_analytic_id.id
			# self.z_invoice_user_id = False
			self.journal_id = self.purchase_id.l10n_in_journal_id.id

		# Copy purchase lines.
		po_lines = self.purchase_id.order_line - self.line_ids.mapped('purchase_line_id')
		new_lines = self.env['account.move.line']
		for line in po_lines.filtered(lambda l: not l.display_type):
		    new_line = new_lines.new(line._prepare_account_move_line(self))
		    new_line.account_id = new_line._get_computed_account()
		    new_line._onchange_price_subtotal()
		    new_lines += new_line
		new_lines._onchange_mark_recompute_taxes()

		# Compute invoice_origin.
		origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
		self.invoice_origin = ','.join(list(origins))
		self.z_invoice_user_id = False


		# Compute ref.
		refs = set(self.line_ids.mapped('purchase_line_id.order_id.partner_ref'))
		refs = [ref for ref in refs if ref]
		self.ref = ','.join(refs)

		# Compute _invoice_payment_ref.
		if len(refs) == 1:
		    self._invoice_payment_ref = refs[0]

		self.purchase_id = False
		self._onchange_currency()

		
class AccountMoveLine(models.Model):
	_inherit = "account.move.line"


	account_analytic_id = fields.Many2one('account.analytic.account',store=True,
		string='Analytic Account',)
	analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
	analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True,
		compute='change_analytic_default',store=True,readonly='0')



	@api.depends('move_id.z_analytic_account_id','product_id','purchase_line_id','move_id.invoice_origin')
	def change_analytic_default(self):
		for line in self:

			if line.move_id:
				# pdb.set_trace()
				line.analytic_account_id 	=line.move_id.z_analytic_account_id.id
			if line.purchase_line_id:
				line.analytic_tag_ids =[(4, analytic_tag.id, None) for analytic_tag in line.purchase_line_id.analytic_tag_ids]
			elif line.move_id.invoice_origin:
				sale_id = self.env['sale.order'].search([('name','=',line.move_id.invoice_origin)])
				sale_line_ids = self.env['sale.order.line'].search([('order_id','=',sale_id.id),('product_id','=',line.product_id.id
					)])
				line.analytic_tag_ids =[(4, analytic_tag.id, None) for analytic_tag in sale_line_ids.analytic_tag_ids]
			# else:
			# 	line.analytic_account_id =False
			# 	line.analytic_tag_ids =False
