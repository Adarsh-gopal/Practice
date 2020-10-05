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



	
class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	order_completed = fields.Boolean(string="Order Completed",store=True,track_visibility='always',compute="onchange_order_completed")
	final_display = fields.Boolean(string="Final Display",default=False)


	
	@api.depends('move_raw_ids.quantity_done')
	def onchange_order_completed(self):
		for line in self:
			for lines in line.move_raw_ids:
				if lines.product_uom_qty != lines.quantity_done:
					lines.raw_material_production_id.order_completed = True
				else:
					lines.raw_material_production_id.order_completed = False

		
	