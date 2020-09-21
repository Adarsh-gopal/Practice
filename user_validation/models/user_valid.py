# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
import json
import re
import uuid
from functools import partial
import itertools
import operator
import psycopg2

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm
from odoo.tools import pycompat
from odoo.exceptions import UserError
from lxml import etree
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode
from collections import namedtuple
import json
import time

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter
from odoo import api, exceptions, fields, models, _
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging
import datetime
from datetime import datetime

class ResUsers(models.Model):
  _inherit = ['res.users']
  sale_order = fields.Boolean('Sale Order',store = True)
  invoice_id = fields.Boolean('Account Invoice',store = True)
  payment_id = fields.Boolean('Payments',store= True)
  product_id = fields.Boolean('Products',store = True)
  customer_id = fields.Boolean('Customers',store = True)
  material_id = fields.Boolean('Approve Requisition',store = True)
  confirm_id = fields.Boolean('Confirm Transfer',store = True)
  journal_id = fields.Boolean('Journal Entry',store = True)
  credit_limit = fields.Boolean('Credit Limit',store=True)
  #read_only = fields.Boolean('Read Only',store = True,default = True)
# class AccountInvoice(models.Model):
# 	_inherit = ['account.invoice']
# 	current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
# 	invoice_id= fields.Boolean('Check',store =True,related = "current_user.invoice_id")

# 	def action_invoice_open(self):
# 		user = self.env.user
# 		if not user.invoice_id:
# 			raise UserError(_('You are not authorized to post the document'))

# 		return super(AccountInvoice, self).action_invoice_open()


	# @api.multi
	# def action_invoice_open(self):
	# 	if self.invoice_id == True:
	# 		to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
	# 		if to_open_invoices.filtered(lambda inv: not inv.partner_id):
	# 			raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
	# 		if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
	# 			raise UserError(_("Invoice must be in draft state in order to validate it."))
	# 		if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
	# 			raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
	# 		if to_open_invoices.filtered(lambda inv: not inv.account_id):
	# 			raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
	# 		to_open_invoices.action_date_assign()
	# 		to_open_invoices.action_move_create()
	# 		return to_open_invoices.invoice_validate()
	# 	else:
	# 		raise models.ValidationError('Your are not authorized to create the document')
	# 	# if self.type != "in_refund":
			
	# 	# 	# lots of duplicate calls to action_invoice_open, so we remove those already open
	# 	# 	to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
	# 	# 	if to_open_invoices.filtered(lambda inv: not inv.partner_id):
	# 	# 		raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
	# 	# 	if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
	# 	# 		raise UserError(_("Invoice must be in draft state in order to validate it."))
	# 	# 	if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
	# 	# 		raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
	# 	# 	if to_open_invoices.filtered(lambda inv: not inv.account_id):
	# 	# 		raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
	# 	# 	to_open_invoices.action_date_assign()
	# 	# 	to_open_invoices.action_move_create()
	# 	# 	return to_open_invoices.invoice_validate()
class AccountJournal(models.Model):
	_inherit = ['account.journal']
	approved_on_ceiling = fields.Boolean('Approval On Ceiling',store = True)
	allowed_limit = fields.Monetary('Allowed Limit',store = True)
	enable_jentry_posting = fields.Boolean('Enable Journal Entry Posting',store = True)


class JournalEntries(models.Model):
	_inherit = ['account.move']
	current_user = fields.Many2one('res.users','Current User')

	def post(self):

		user = self.env.user
		if not self.journal_id.enable_jentry_posting:
			if not user.journal_id:
				raise UserError(_('You are not authorized to post the document'))

		return super(JournalEntries, self).post()
	# journal_entry= fields.Boolean('Journal Entry',store =True,related = "current_user.journal_id")
	# show_post= fields.Boolean(compute="_compute_show_post")
	# show_post_jv= fields.Boolean(compute="_compute_show_post_jv")

	# show_post= fields.Boolean(compute='_get_show')

	# @api.multi
	# def _get_show(self):
	# 	for line in self:
	# 		line.show_post = lambda self: self.env.user.journal_id
	# 		line.current_user = lambda self: self.env.user

	# @api.multi
	# @api.depends
	# def _compute_hide_post(self):
	# 	for line in self:
	# 		line.hide_post = not line.current_user.journal_id

	# @api.multi
	# @api.depends('journal_entry')
	# def _compute_show_post_jv(self):
	# 	self.show_post_jv = self.journal_entry

	# @api.multi
	# @api.depends('journal_entry')
	# def _compute_show_post(self):
	# 	if self.journal_entry == True:
	# 		self.show_post = False
	# 	else:
	# 		self.show_post = True
	# journal_posting = fields.Boolean('Journal Entry Posting',store = True,related = 'journal_id.enable_jentry_posting')

	# @api.multi
	# def post(self):
	# 	if self.journal_posting == True:
	# 		if self.journal_entry == True:
	# 			invoice = self._context.get('invoice', False)
	# 			self._post_validate()
	# 			for move in self:
	# 				move.line_ids.create_analytic_lines()
	# 				if move.name == '/':
	# 					new_name = False
	# 					journal = move.journal_id

	# 					if invoice and invoice.move_name and invoice.move_name != '/':
	# 						new_name = invoice.move_name
	# 					else:
	# 						if journal.sequence_id:
	# 							sequence = journal.sequence_id
	# 							if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
	# 								if not journal.refund_sequence_id:
	# 									raise UserError(_('Please define a sequence for the credit notes'))
	# 								sequence = journal.refund_sequence_id

	# 							new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
	# 						else:
	# 							raise UserError(_('Please define a sequence on the journal.'))

	# 					if new_name:
	# 						move.name = new_name
	# 			return self.write({'state': 'posted'})
	# 		else:
	# 			raise models.ValidationError('You are not authorized to create journal entry')
	# 	else:
	# 		invoice = self._context.get('invoice', False)
	# 		self._post_validate()
	# 		for move in self:
	# 			move.line_ids.create_analytic_lines()
	# 			if move.name == '/':

	# 				new_name = False
	# 				journal = move.journal_id

	# 				if invoice and invoice.move_name and invoice.move_name != '/':
	# 					new_name = invoice.move_name
	# 				else:
	# 					if journal.sequence_id:
	# 						sequence = journal.sequence_id
	# 						if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
	# 							if not journal.refund_sequence_id:
	# 								raise UserError(_('Please define a sequence for the credit notes'))
	# 							sequence = journal.refund_sequence_id

	# 						new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
	# 					else:
	# 						raise UserError(_('Please define a sequence on the journal.'))

	# 				if new_name:
	# 					move.name = new_name
	# 		return self.write({'state': 'posted'})


class AccountPayment(models.Model):
	_inherit = ['account.payment']
	allowed_limit = fields.Monetary('Approved On Ceiling',store = True,related = 'journal_id.allowed_limit')
	approved_on_ceiling = fields.Boolean('Approval On Ceiling',store = True,related = 'journal_id.approved_on_ceiling')
	current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
	check_payment= fields.Boolean('Allow Payment',store =True,related = "current_user.payment_id",readonly=False)

	def post(self):

		user = self.env.user
		if not user.payment_id:
			raise UserError(_('You are not authorized to post the document'))

		if self.journal_id.approved_on_ceiling == True:
			if self.amount >= self.allowed_limit:
				raise UserError('Payment limit exceeded, you are not authorized')

		return super(AccountPayment, self).post()


# class AccountPayment(models.Model):
# 	_inherit = ['account.payment']
# 	allowed_limit = fields.Monetary('Approved On Ceiling',store = True,related = 'journal_id.allowed_limit')
# 	approved_on_ceiling = fields.Boolean('Approval On Ceiling',store = True,related = 'journal_id.approved_on_ceiling')
# 	current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
# 	check_payment= fields.Boolean('Check',store =True,related = "current_user.payment_id")
# 	@api.multi
# 	def post(self):
# 		for rec in self:
# 			if rec.check_payment == True:
# 				if rec.journal_id.approved_on_ceiling == True:
# 					if rec.amount <= rec.allowed_limit and rec.journal_id.approved_on_ceiling == True:
# 						if rec.state != 'draft':
# 							raise UserError(_("Only a draft payment can be posted."))

# 						if any(inv.state != 'open' for inv in rec.invoice_ids):
# 							raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

# 						# keep the name in case of a payment reset to draft
# 						if rec.name:
# 							# Use the right sequence to set the name
# 							if rec.payment_type == 'transfer':
# 								sequence_code = 'account.payment.transfer'
# 							else:
# 								if rec.partner_type == 'customer':
# 									if rec.payment_type == 'inbound':
# 										sequence_code = 'account.payment.customer.invoice'
# 									if rec.payment_type == 'outbound':
# 										sequence_code = 'account.payment.customer.refund'
# 								if rec.partner_type == 'supplier':
# 									if rec.payment_type == 'inbound':
# 										sequence_code = 'account.payment.supplier.refund'
# 									if rec.payment_type == 'outbound':
# 										sequence_code = 'account.payment.supplier.invoice'
# 							rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
# 							if not rec.name and rec.payment_type != 'transfer':
# 								raise UserError("You have to define a sequence for %s in your company.") % (sequence_code,)
# 						# Create the journal entry
# 						amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
# 						move = rec._create_payment_entry(amount)

# 						# In case of a transfer, the first journal entry created debited the source liquidity account and credited
# 						# the transfer account. Now we debit the transfer account and credit the destination liquidity account.
# 						if rec.payment_type == 'transfer':
# 							transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
# 							transfer_debit_aml = rec._create_transfer_entry(amount)
# 							(transfer_credit_aml + transfer_debit_aml).reconcile()

# 						rec.write({'state': 'posted', 'move_name': move.name})
# 					else:
# 						raise models.ValidationError('Payment limit exceeded, you are not authorized')
# 				else:
# 					if rec.state != 'draft':
# 						raise UserError(_("Only a draft payment can be posted."))

# 					if any(inv.state != 'open' for inv in rec.invoice_ids):
# 						raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
# #====================================================================================================================================================
# 					# keep the name in case of a payment reset to draft
# 					if rec.name:
# 						# Use the right sequence to set the name
# 						if rec.payment_type == 'transfer':
# 							sequence_code = 'account.payment.transfer'
# 						else:
# 							if rec.partner_type == 'customer':
# 								if rec.payment_type == 'inbound':
# 									sequence_code = 'account.payment.customer.invoice'
# 								if rec.payment_type == 'outbound':
# 									sequence_code = 'account.payment.customer.refund'
# 							if rec.partner_type == 'supplier':
# 								if rec.payment_type == 'inbound':
# 									sequence_code = 'account.payment.supplier.refund'
# 								if rec.payment_type == 'outbound':
# 									sequence_code = 'account.payment.supplier.invoice'
# 						rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
# 						if not rec.name and rec.payment_type != 'transfer':
# 							raise UserError("You have to define a sequence for %s in your company.") % (sequence_code,)
# 					# Create the journal entry
# 					amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
# 					move = rec._create_payment_entry(amount)

# 					# In case of a transfer, the first journal entry created debited the source liquidity account and credited
# 					# the transfer account. Now we debit the transfer account and credit the destination liquidity account.
# 					if rec.payment_type == 'transfer':
# 						transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
# 						transfer_debit_aml = rec._create_transfer_entry(amount)
# 						(transfer_credit_aml + transfer_debit_aml).reconcile()

# 					rec.write({'state': 'posted', 'move_name': move.name})		
# 			else:
# 				raise models.ValidationError('You are not authorized to create payments')

# 		return True
# class ProductTemplate(models.Model):
# 	_inherit = ['product.template']
# 	current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
# 	check_product = fields.Boolean('Check',store =True,related = "current_user.product_id")
# 	@api.model_create_multi
# 	def create(self, vals_list):
# 		''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
# 		# TDE FIXME: context brol
# 		for vals in vals_list:
# 			tools.image_resize_images(vals)
# 		templates = super(ProductTemplate, self).create(vals_list)
# 		if "create_product_product" not in self._context:
# 			templates.with_context(create_from_tmpl=True).create_variant_ids()

# 		# This is needed to set given values to first variant after creation
# 		for template, vals in pycompat.izip(templates, vals_list):
# 			related_vals = {}
# 			if templates['check_product'] == True:
# 				if vals.get('barcode'):
# 					related_vals['barcode'] = vals['barcode']
# 				if vals.get('default_code'):
# 					related_vals['default_code'] = vals['default_code']
# 				if vals.get('standard_price'):
# 					related_vals['standard_price'] = vals['standard_price']
# 				if vals.get('volume'):
# 					related_vals['volume'] = vals['volume']
# 				if vals.get('weight'):
# 					related_vals['weight'] = vals['weight']
# 				if related_vals:
# 					template.write(related_vals)
# 			else:
# 				raise models.ValidationError('You are not authorized to create product')
# 		return templates
# 	@api.multi
# 	def create_variant_ids(self):
# 		Product = self.env["product.product"]
# 		AttributeValues = self.env['product.attribute.value']

# 		variants_to_create = []
# 		variants_to_activate = []
# 		variants_to_unlink = []

# 		for tmpl_id in self.with_context(active_test=False):
# 			# adding an attribute with only one value should not recreate product
# 			# write this attribute on every product to make sure we don't lose them
# 			variant_alone = tmpl_id.attribute_line_ids.filtered(lambda line: line.attribute_id.create_variant == 'always' and len(line.value_ids) == 1).mapped('value_ids')
# 			for value_id in variant_alone:
# 				updated_products = tmpl_id.product_variant_ids.filtered(lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
# 				updated_products.write({'attribute_value_ids': [(4, value_id.id)]})
# 			# iterator of n-uple of product.attribute.value *ids*
# 			variant_matrix = [
# 				AttributeValues.browse(value_ids)
# 				for value_ids in itertools.product(*(line.value_ids.ids for line in tmpl_id.attribute_line_ids if line.value_ids[:1].attribute_id.create_variant != 'no_variant'))
# 			]

# 			# get the value (id) sets of existing variants
# 			existing_variants = {frozenset(variant.attribute_value_ids.filtered(lambda r: r.attribute_id.create_variant != 'no_variant').ids) for variant in tmpl_id.product_variant_ids}
# 			# -> for each value set, create a recordset of values to create a
# 			#    variant for if the value set isn't already a variant
# 			for value_ids in variant_matrix:
# 				if set(value_ids.ids) not in existing_variants and not any(value_id.attribute_id.create_variant == 'dynamic' for value_id in value_ids):
# 					variants_to_create.append({
# 						'product_tmpl_id': tmpl_id.id,
# 						'attribute_value_ids': [(6, 0, value_ids.ids)]
# 					})

# 			if len(variants_to_create) > 1000:
# 				raise UserError(_("""
# 				The number of variants to generate is too high.
# 				You should either not generate variants for each combination or generate them on demand from the sales order.
# 				To do so, open the form view of attributes and change the mode of *Create Variants*."""))

# 			# check product
# 			for product_id in tmpl_id.product_variant_ids:
# 				if not product_id.active and product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.create_variant != 'no_variant') in variant_matrix:
# 					variants_to_activate.append(product_id)
# 				elif product_id.attribute_value_ids.filtered(lambda r: r.attribute_id.create_variant != 'no_variant') not in variant_matrix:
# 					variants_to_unlink.append(product_id)

# 		if variants_to_activate:
# 			Product.concat(*variants_to_activate).write({'active': True})

# 		# create new products
# 		if variants_to_create:
# 			Product.create(variants_to_create)

# 		# unlink or inactive product
# 		for variant in variants_to_unlink:
# 			try:
# 				with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
# 					variant.unlink()
# 			# We catch all kind of exception to be sure that the operation doesn't fail.
# 			except (psycopg2.Error, except_orm):
# 				variant.write({'active': False})
# 				pass
# 		return True
# 	@api.multi
# 	def write(self, vals):
# 		tools.image_resize_images(vals)
# 		res = super(ProductTemplate, self).write(vals)
# 		if res['check_product'] == True:
# 			if 'attribute_line_ids' in vals or vals.get('active'):
# 				self.create_variant_ids()
# 			if 'active' in vals and not vals.get('active'):
# 				self.with_context(active_test=False).mapped('product_variant_ids').write({'active': vals.get('active')})
# 			return res
# 		else:
# 			raise models.ValidationError('You are not authorized to create product')
# class ProductProduct(models.Model):
# 	_inherit = 'product.product'
# 	current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
# 	check_product = fields.Boolean('Check',store =True,related = "current_user.product_id")
# 	@api.model_create_multi
# 	def create(self, vals_list):
# 		products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
# 		if products['check_product'] == True:
# 			for product, vals in pycompat.izip(products, vals_list):
# 				# When a unique variant is created from tmpl then the standard price is set by _set_standard_price
# 				if not (self.env.context.get('create_from_tmpl') and len(product.product_tmpl_id.product_variant_ids) == 1):
# 					product._set_standard_price(vals.get('standard_price') or 0.0)
# 			return products
# 		else:
# 			raise models.ValidationError('You are not authorized to create product')
# class Partner(models.Model):
# 	_inherit = 'res.partner'
# 	current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
# 	check_product = fields.Boolean('Check',store =True,related = "current_user.customer_id")
# 	@api.model_create_multi
# 	def create(self, vals_list):
# 		for vals in vals_list:
# 			if vals.get('website'):
# 				vals['website'] = self._clean_website(vals['website'])
# 			if vals.get('parent_id'):
# 				vals['company_name'] = False
# 			# compute default image in create, because computing gravatar in the onchange
# 			# cannot be easily performed if default images are in the way
# 			if not vals.get('image'):
# 				vals['image'] = self._get_default_image(vals.get('type'), vals.get('is_company'), vals.get('parent_id'))
# 			tools.image_resize_images(vals, sizes={'image': (1024, None)})
# 		partners = super(Partner, self).create(vals_list)
# 		if partners['check_product'] == True:
# 			for partner, vals in pycompat.izip(partners, vals_list):
# 				partner._fields_sync(vals)
# 				partner._handle_first_contact_creation()
# 			return partners
# 		else:
# 			raise models.ValidationError('You are not authorized to create customer')
class SaleOrder(models.Model):
	_inherit = ['sale.order']

	def action_confirm(self):

		user = self.env.user
		if not user.sale_order:
			# import pdb
			# pdb.set_trace()
			raise UserError(_('You are not authorized to post the document'))

		return super(SaleOrder, self).action_confirm()

	def over_credit(self):
		check = super(SaleOrder, self).over_credit()
		user = self.env.user
		if not user.credit_limit:
			# import pdb
			# pdb.set_trace()
			raise UserError(_('You are not authorized to Allow the Credit Limit'))

		return check

	# def action_info(self):
	# 	check = super(SaleOrder, self).action_info()
	# 	user = self.env.user
	# 	if not user.credit_limit:
	# 		# import pdb
	# 		# pdb.set_trace()
	# 		raise UserError(_('You are not authorized to Access the Credit Information'))

	# 	return check


	current_user = fields.Many2one('res.users','Current User')
	check_sale = fields.Boolean('Check')

	# @api.multi
	# def action_confirm(self):
	# 	if self.check_sale == True:
	# 		self._action_confirm()
	# 		if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
	# 			self.action_done()
	# 		return True
	# 	else:
	# 		raise models.ValidationError('You are not authorized to confirm sale')

# class IndentOrder(models.Model):
# 	_inherit = 'stock.indent.order'
# 	current_user = fields.Many2one('res.users','Current User')

# 	def button_indent_confirm_approve(self):

# 		user = self.env.user
# 		if not user.material_id:
# 			raise UserError(_('You are not authorized to confirm the document'))

# 		return super(IndentOrder, self).button_indent_confirm_approve()


# 	def indent_transfer_move_confirm_new(self):

# 		user = self.env.user
# 		if not user.confirm_id:
# 			raise UserError(_('You are not authorized to confirm the document'))

# 		return super(IndentOrder, self).indent_transfer_move_confirm_new()



	# check_material = fields.Boolean('Check',compute = 'check_alpha_1')
	# check_confirm = fields.Boolean('Check',compute = 'check_alpha_1')
	# check_current = fields.Boolean('Check',store = True)
	# def check_alpha(self):
	# 	for line in self:
	# 		check = self.env.uid
	# 		line.current_user = check
	# 		line.check_material = line.current_user.material_id
	# 		line.check_confirm = line.current_user.confirm_id
	# @api.depends('current_user')
	# def check_alpha_1(self):
	# 	for line in self:
	# 		line.check_material = check = line.current_user.material_id
	# 		line.check_confirm = check = line.current_user.confirm_id

	# @api.one
	# def button_indent_confirm_approve(self):
	# 	todo = []
	# 	if self.check_material == True:
	# 		for o in self:
	# 			if not any(line for line in o.product_lines):
	# 				raise exceptions.Warning(_('Error!'),
	#                               _('You cannot Approve a order without any order line.'))
	# 			for line in o.product_lines:
	# 				if line:
	# 					todo.append(line.id)

	# 		appr_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	# 		self.env['indent.order.line'].action_confirm(todo)

	# 		for id in self.ids:
	# 			self.write({'state': 'inprogress', 'approve_date': appr_date})
	# 		return True
	# 	else:
	# 		raise models.ValidationError('You are not authorized to confirm Approve reqquisition material')

	# @api.multi
	# def indent_transfer_move_confirm_new(self):
	# 	if self.check_confirm == True:
	# 		StockPicking = self.env['stock.picking']
	# 		for order in self:
	# 			if any([order.product_lines.mapped('product_id.type')]):
	# 				res = order._prepare_pickings()
	# 				picking = StockPicking.create(res)
	# 				moves = order.product_lines._create_stock_moves(picking)
	# 		self.write({'state': 'done'})
	# 		return True
	# 	else:
	# 		raise models.ValidationError('You are not authorized to confirm')



	


