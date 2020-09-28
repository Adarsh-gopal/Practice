# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from collections import defaultdict

# from odoo import api, fields, models, tools, _
# from odoo.addons import decimal_precision as dp
# from odoo.addons.stock_landed_costs.models import product
# from odoo.exceptions import UserError

from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class LandedCost(models.Model):
	_inherit = 'stock.landed.cost'

	z_account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="The analytic account related to a sales order.")



	#commented coz of installation of 3rd party purchased app ' dev_landed_cost_average_price'
	
	def button_validate(self):
		
		if any(cost.state != 'draft' for cost in self):
		    raise UserError(_('Only draft landed costs can be validated'))
		if not all(cost.picking_ids for cost in self):
		    raise UserError(_('Please define the transfers on which those additional costs should apply.'))
		cost_without_adjusment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
		if cost_without_adjusment_lines:
		    cost_without_adjusment_lines.compute_landed_cost()
		if not self._check_sum():
		    raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

		for cost in self:
		    move = self.env['account.move']
		    move_vals = {
		        'journal_id': cost.account_journal_id.id,
		        'date': cost.date,
		        'ref': cost.name,
		        'line_ids': [],
		        'z_analytic_account_id':cost.z_account_analytic_id.id,
		        'type': 'entry',
		    }
		    for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
		        remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
		        linked_layer = line.move_id.stock_valuation_layer_ids[:1]  # Maybe the LC layer should be linked to multiple IN layer?

		        # Prorate the value at what's still in stock
		        cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
		        if not cost.company_id.currency_id.is_zero(cost_to_add):
		            valuation_layer = self.env['stock.valuation.layer'].create({
		                'value': cost_to_add,
		                'unit_cost': 0,
		                'quantity': 0,
		                'remaining_qty': 0,
		                'stock_valuation_layer_id': linked_layer.id,
		                'description': cost.name,
		                'stock_move_id': line.move_id.id,
		                'product_id': line.move_id.product_id.id,
		                'stock_landed_cost_id': cost.id,
		                'company_id': cost.company_id.id,
		            })
		            move_vals['stock_valuation_layer_ids'] = [(6, None, [valuation_layer.id])]
		            linked_layer.remaining_value += cost_to_add
		        # Update the AVCO
		        product = line.move_id.product_id
		        if product.cost_method == 'average' and not float_is_zero(product.quantity_svl, precision_rounding=product.uom_id.rounding):
		            product.with_context(force_company=self.company_id.id).sudo().standard_price += cost_to_add / product.quantity_svl
		        # `remaining_qty` is negative if the move is out and delivered proudcts that were not
		        # in stock.
		        qty_out = 0
		        if line.move_id._is_in():
		            qty_out = line.move_id.product_qty - remaining_qty
		        elif line.move_id._is_out():
		            qty_out = line.move_id.product_qty
		        move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)

		    move = move.create(move_vals)
		    cost.write({'state': 'done', 'account_move_id': move.id})
		    move.post()

		    if cost.vendor_bill_id and cost.vendor_bill_id.state == 'posted' and cost.company_id.anglo_saxon_accounting:
		        all_amls = cost.vendor_bill_id.line_ids | cost.account_move_id.line_ids
		        for product in cost.cost_lines.product_id:
		            accounts = product.product_tmpl_id.get_product_accounts()
		            input_account = accounts['stock_input']
		            all_amls.filtered(lambda aml: aml.account_id == input_account).reconcile()
		return True

