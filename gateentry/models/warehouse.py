from odoo import models, fields,api
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

import logging

_logger = logging.getLogger(__name__)



class Warehouse(models.Model):
	_inherit = "stock.warehouse"
	gate_entry_required = fields.Boolean('Gate Entry Required', default=False)

	
class GateEntrySelection(models.Model):
	_inherit = "stock.picking"

	sale_id = fields.Many2one('sale.order',string="Sales order")
	purchase_id = fields.Many2one('purchase.order',string="Purchase Order",readonly=False)

	gate_entry_attach_inward = fields.Many2one('gateentry.inward',string='Attach Gate Entry IN',domain="['|',('sales_return_order_ids.so_name', '=', sale_id),('purchase_order_ids.purchase_source_no', '=', purchase_id)]")
	gate_entry_attach_outward = fields.Many2one('gateentry.outward',string='Attach Gate Entry Out',domain="['|',('purchase_return_order_outward_ids.po_name', '=', purchase_id),('sale_order_outward_ids.source_no', '=', name)]")
	gate_check_inward = fields.Boolean('Gate Bool', default=False,compute="_find_gate")
	gate_check_outward = fields.Boolean('Gate Bool', default=False,compute="_find_gate")
	gate_check_internal = fields.Boolean('Gate Bool', default=False,compute="_find_gate_internal")
	z_vehicle_no = fields.Many2one('fleet.vehicle',string="Vehicle No")
	z_driver = fields.Many2one('hr.employee',string="Driver",domain="[('job_id','=','DRIVER')]")
	z_cleaner = fields.Many2one('hr.employee',string="Cleaner",domain="[('job_id','=','CLEANER')]")

	@api.depends('gate_check_inward','gate_check_outward')
	def _find_gate(self):
		#this condition is used to check whether a gate entry number should be attached or not based on the operation type
		for line in self:
			if line.picking_type_id.warehouse_id.gate_entry_required == True:
				if line.picking_type_id.id != 2:
					line.gate_check_inward = True
					line.gate_check_outward = False
				else:
					line.gate_check_inward = False
					line.gate_check_outward = True
			else:
				line.gate_check_inward = False
				line.gate_check_outward = False

	@api.depends('sale_id','purchase_id')
	def _find_gate_internal(self):
		#this condition is used to check whether a gate entry number should be attached or not based on the operation type
		for line in self:
			line.gate_check_internal = False
			if not line.purchase_id:
				line.gate_check_internal = True
				
	
	def button_validate(self):
		if self.weighment_id.reference == self.origin:
			if not self.weighment_id.state == 'release' and not self.weighment_id.state == 'close':
				raise UserError(_('Weighment is not Completed/Closed for this Manufacturing Order. Complete the Weighment and come back...'))
			elif self.weighment_id.state == 'close' and not self.weighment_id.reason:
				raise UserError(_('Weighment is Closed but Reason is not Updated. Please Update the Reason and come back...'))
			else:
				self.ensure_one()
				for line in self:
					if self.purchase_id:
						ref_ids = self.env['gateentry.outward'].search([('id', '=', self.gate_entry_attach_outward.id)])
						if ref_ids:
							for line in ref_ids.purchase_return_order_outward_ids:
								line.update({'reference': self.id
									})
					if self.sale_id:
						so_ref_ids = self.env['gateentry.inward'].search([('id', '=', self.gate_entry_attach_inward.id)])
						if so_ref_ids:
							for line in so_ref_ids.sales_return_order_ids:
								line.update({'reference': self.id
									})

		else:
			self.ensure_one()
			for line in self:
				if self.purchase_id:
					ref_ids = self.env['gateentry.outward'].search([('id', '=', self.gate_entry_attach_outward.id)])
					if ref_ids:
						for line in ref_ids.purchase_return_order_outward_ids:
							line.update({'reference': self.id
								})
				if self.sale_id:
					so_ref_ids = self.env['gateentry.inward'].search([('id', '=', self.gate_entry_attach_inward.id)])
					if so_ref_ids:
						for line in so_ref_ids.sales_return_order_ids:
							line.update({'reference': self.id
								})
			
		return super(GateEntrySelection, self).button_validate()
	           

class WarehouseEmployee(models.Model):
	_name = "gateentry.warehouse.users"

	name = fields.Many2one('res.users',string='User')
	warehouse_ids = fields.One2many('gateentry.warehouse','warehouse_id')

class GateentryWarehouse(models.Model):
	_name = "gateentry.warehouse"

	warehouse_id = fields.Many2one('gateentry.warehouse.users',string="Warehouse")

	name = fields.Many2one('stock.location',string='Warehouse')
	current_user = fields.Many2one('res.users',string='User',related="warehouse_id.name")
	default_field = fields.Boolean('Set as default', default=False)

class GateentryFleet(models.Model):
	_inherit = "fleet.vehicle.odometer"

	date = fields.Datetime('Date',readonly=True,default=fields.Datetime.now)