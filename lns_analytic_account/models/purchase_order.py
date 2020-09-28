# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
import pdb


class PurchaseOrder(models.Model):
	_inherit = "purchase.order"
	
	#inherited field to make readonly false
	z_account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', 
		states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
		,store = True,compute='get_aa_from_dropship')


	@api.depends('picking_type_id')
	def get_aa_from_dropship(self):
		for l in self:
			if l.origin:
				sale_id = self.env['sale.order'].search([('name','=',l.origin)])
				l.z_account_analytic_id = sale_id.analytic_account_id.id
			


	
	# Get the Analytic Account from warehouse 
	# @api.onchange('picking_type_id')
	# def get_aa(self):
	# 	for l in self:
	# 		if l.picking_type_id:
	# 			l.z_account_analytic_id = l.picking_type_id.warehouse_id.z_account_analytic_id.id
				
	# Get the Analytic Account from warehouse 
	# @api.onchange('z_account_analytic_id')
	# def AA_From_Picking(self):
	# 	for l in self:
	# 		if l.z_account_analytic_id:
	# 			l.z_account_analytic_id = l.picking_type_id.warehouse_id.z_account_analytic_id.id


	
	def action_view_invoice(self):
		action = self.env.ref('account.action_move_in_invoice_type')
		result = action.read()[0]
		create_bill = self.env.context.get('create_bill', False)
		result['context'] = {
		#'type': 'in_invoice',
		'default_type': 'in_invoice',
		'default_purchase_id': self.id,
		#'default_currency_id': self.currency_id.id,
		'default_company_id': self.company_id.id,
		'default_z_analytic_account_id':self.z_account_analytic_id.id,
		#'company_id': self.company_id.id
		}
		if len(self.invoice_ids) > 1 and not create_bill:
			result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
		else:
			res = self.env.ref('account.view_move_form', False)
			form_view = [(res and res.id or False, 'form')]
			if 'views' in result:
				result['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
			else:
				result['views'] = form_view
			# Do not set an invoice_id if we want to create a new bill.
			if not create_bill:
				result['res_id'] = self.invoice_ids.id or False
		result['context']['default_origin'] = self.name
		result['context']['default_reference'] = self.partner_ref
		return result

	
	def button_confirm(self):
		if not self.z_account_analytic_id:
			raise UserError(_('Kindly select the Analytic Account before confirming this Purchase order'))
		return super(PurchaseOrder, self).button_confirm()


	

class PurchaseOrderLine(models.Model):
	_inherit = "purchase.order.line"

	#new field added.. account_analytic_id is used to display in the front end. But the value is flowing in the function create_invoices
	account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', store=True,compute='change_analytic_default')
	analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

	
	@api.depends('order_id.z_account_analytic_id','product_id')
	def change_analytic_default(self):
		for line in self:
			line.account_analytic_id = line.order_id.z_account_analytic_id.id

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    z_account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account',store = True)


    