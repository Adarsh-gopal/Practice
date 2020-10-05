# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
#from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.addons import decimal_precision as dp



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sale Order'

    sale_weigh_lines = fields.One2many('weighment.product', 'sale_line_id', string="Weighment", readonly=True, copy=False)
    order_completed = fields.Boolean(string="Order Completed",invisible=True,store=True,track_visibility='always')

    @api.onchange('product_id')
    def compute_order_complete(self):
    	for line in self:
    		line.order_completed = True


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	order_completed = fields.Boolean(string="Order Completed",invisible=True,store=True,track_visibility='always',compute="onchange_order_completed")
	final_display = fields.Boolean(string="Final Display",default=False)


	
	@api.depends('order_line.qty_delivered')
	def onchange_order_completed(self):
		self.order_completed = True
		for line in self:
			for lines in line.order_line:
				if lines.product_uom_qty != lines.qty_delivered:
					lines.order_id.order_completed = True
				else:
					lines.order_id.order_completed = False

		
