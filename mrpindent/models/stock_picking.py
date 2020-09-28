# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

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
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_utils, float_compare

class StockPicking(models.Model):
	_inherit = "stock.picking"
	
	z_operator = fields.Char(string='Operator',copy=False,store=True,compute="compute_display_operator_name")
	z_workcenter_id = fields.Many2one('mrp.workcenter',string="Machine Number",copy=False,store=True,compute="compute_display_operator_name")
	z_shift = fields.Many2one('resource.calendar',string="Shift",copy=False,store=True,compute="compute_display_operator_name")


	
	@api.depends('origin')
	def compute_display_operator_name(self):
		for line in self:
			mo_order = self.env['mrp.production'].search([('name', '=', line.origin)])
			if mo_order:
				line.z_operator = mo_order.logger_name
				line.z_shift = mo_order.shift.id
				line.z_workcenter_id = mo_order.workcenter_id.id

