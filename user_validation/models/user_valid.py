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
  #read_only = fields.Boolean('Read Only',store = True,default = True)
class AccountInvoice(models.Model):
	_inherit = ['account.move']
	current_user = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
	invoice_id= fields.Boolean('Check',store =True,related = "current_user.invoice_id")

	
	def action_invoice_open(self):
		user = self.env.user
		if not user.invoice_id:
			raise UserError(_('You are not authorized to post the document'))

		return super(AccountInvoice, self).action_invoice_open()


	
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



class SaleOrder(models.Model):
	_inherit = ['sale.order']

	
	def action_confirm(self):

		user = self.env.user
		if not user.sale_order:
			import pdb
			pdb.set_trace()
			raise UserError(_('You are not authorized to post the document'))

		return super(SaleOrder, self).action_confirm()


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

class IndentOrder(models.Model):
	_inherit = 'stock.indent.order'
	current_user = fields.Many2one('res.users','Current User')

	
	def button_indent_confirm_approve(self):

		user = self.env.user
		if not user.material_id:
			raise UserError(_('You are not authorized to confirm the document'))

		return super(IndentOrder, self).button_indent_confirm_approve()


	
	def indent_transfer_move_confirm_new(self):

		user = self.env.user
		if not user.confirm_id:
			raise UserError(_('You are not authorized to confirm the document'))

		return super(IndentOrder, self).indent_transfer_move_confirm_new()



	


	


