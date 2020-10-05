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




class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order'

    purchase_weigh_lines = fields.One2many('weighment.product', 'purchase_line_id', string="Weighment", readonly=True, copy=False)



class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	order_completed = fields.Boolean(string="Order Completed",invisible=True,store=True,track_visibility='always',compute="onchange_order_completed")
	final_display = fields.Boolean(string="Final Display",default=False)


	
	@api.depends('order_line.qty_received')
	def onchange_order_completed(self):
		for line in self:
			line.order_completed = True
			for lines in line.order_line:
				if lines.product_qty != lines.qty_received:
					line.order_completed = True
				else:
					line.order_completed = False
				

		
			

