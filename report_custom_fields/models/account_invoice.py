# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from odoo import api, fields, models, _
class AccountInvoice(models.Model):
	_inherit = 'account.move'
	payment_method = fields.Char(string='Payment method',store=True)
	ext_doc_no = fields.Char(string='External Document No', store=True)
	order_type = fields.Char(string='Order Type',store=True)
	custom_po_no = fields.Char(string='PO No', store=True)
	po_date = fields.Date(String='PO Date', store=True)
	vehicle = fields.Many2many('fleet.vehicle',string='Vehicle')
	confirmation_date = fields.Datetime(string='Confirmation Date')
	#Export related fields
	port_of_discharge = fields.Many2one('port.order', string='Port Of Discharge')
	port_of_destination = fields.Many2one('port.order', string='Port Of Destination')
	country_of_origin_goods = fields.Many2one('res.country', string='Country Of Origin Of Goods')
	country_of_final_destination = fields.Many2one('res.country', string='Country Of Final Destination')
	pre_carriage= fields.Selection([
        ('air', 'By Air'),
        ('rail', 'Rail'),
        ('road', 'Road')], string='Pre Carriage')
	carriage= fields.Selection([
        ('sea', 'Sea')], string='Carriage')
	export_shipment_method = fields.Many2one('export.shipment', string='Export Shipment Method')
	type_of_container = fields.Many2one('type.container', string='Type Of Container')
	ext_vehicle_no = fields.Char(string="External Vehicle No.")
	transporter = fields.Char(string="Dispatched Through")
	lr_no = fields.Char(string="LR No")
	proforma_sequence = fields.Char(string="Proforma Invoice Number",readonly=True)
	z_delivered_to = fields.Char(string="Delivered To")
	e_way_no = fields.Char(string='E-way Bill No', store=True)
	# z_string = fields.Text(string="All Picking references",compute='get_string')

	def get_string(self):
		delivery_mer = 0
		z_string = 0
		for line in self:
			if line.origin:
				sale_order = line.origin.split(", ")
				for delivery in self.env['stock.picking'].search([('sale_id.name', '=', sale_order),('state','=','done')],order="name asc"):
					if delivery.name:
						z_string = delivery.name
						delivery_mer = str(z_string)+ ', '+ str(delivery_mer)
					line.z_string = delivery_mer.strip(", 0")


	# @api.depends('picking_ids')
	# def get_string(self):
	# 	for line in self:
	# 		sale_order = line.origin
	# 		order_line = self.env['stock.picking'].search([('sale_id.name', '=', sale_order),('state','=','done')])
	# 		totals = {}
	# 		for record in order_line:
	# 			totals[record.name] = totals.get(record.name,0)
	# 			sort_total = sorted(list(totals.items()), key=lambda r: r[1], reverse=True)
	# 		return_val['totals'] = sort_total[0:3]


	# def get_string(self):
	# 	for lin in self:
	# 		for line in self.picking_ids.search([('sale_id.name', '=', sale_order),('state','=','done')],order="name asc"):
	# 			lin.z_string = line.name

	@api.onchange('ext_vehicle_no')
	def set_upper(self):
		if self.ext_vehicle_no:
			self.ext_vehicle_no = str(self.ext_vehicle_no).upper()   
			return


class AccountInvoice(models.Model):
	_inherit = 'account.move.line'
	
	l10n_in_hsn = fields.Char('HSN Code', store=True)