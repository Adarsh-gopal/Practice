# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
import pdb
class StockProductionLot(models.Model):
	_inherit = "stock.production.lot"

	z_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',compute='get_analytic_tgas')
	# Overiding the existing file for store the data in db
	purchase_order_ids = fields.Many2many('purchase.order', string="Purchase Orders", compute='_compute_purchase_order_ids', readonly=True, store=True)


	@api.depends('purchase_order_ids','name')
	def get_analytic_tgas(self):
		for l in self:
			stock_moves = self.env['stock.move.line'].search([
				('lot_id', '=', l.id),
				('state', '=', 'done')
				])
			if stock_moves:
				for each_move in stock_moves:
					if each_move.product_id.id == l.product_id.id:
						l.z_analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in each_move.z_analytic_tag_ids]
			else:
				l.z_analytic_tag_ids = False

            