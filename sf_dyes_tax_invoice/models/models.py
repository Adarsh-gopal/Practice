# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from num2words import num2words

class Partner(models.Model):
	_inherit = 'account.move'

	destination = fields.Char(string='Destination')

	invoice_incoterm_id = fields.Many2one('account.incoterms',compute="incoterms")

	@api.depends('partner_id')
	def incoterms(self):
		for rec in self:
			if rec.partner_id.incoterms:
				rec.invoice_incoterm_id = rec.partner_id.incoterms
			else:
				rec.invoice_incoterm_id = None
				
	@api.onchange('partner_id')
	def Onchange_destination(self):
		for l in self:
			l.destination = l.partner_id.city

	def amt_in_words_ti(self, amount):
		amount1=str(amount)
		amt= amount1.split(".")
		if int(amt[1]) > 0:
			second_part = ' Rupees and '+ num2words(int(amt[1]), lang='en_IN').capitalize() + ' Paise only '
		else:
			second_part = ' Rupees Only '

		return num2words(int(amt[0]), lang='en_IN').capitalize() + second_part

	def saleno(self,origin):
		saleno=self.env['sale.order'].search([('name','=',origin)], limit=1)
		if saleno:
			return saleno.warehouse_id.partner_id

	def deliverydate(self,origin):
		dd=self.env['sale.order'].search([('name','=',origin)])
		if dd:
			return dd.commitment_date

			# added to get iot_id(03-06-2020)

	# def _get_invoiced_lot_values(self):
	# 	# to take diffrent product wit lot no.(panther)
	# 	for l in self.invoice_line_ids:
	# 		# store and check check condition in variable

	# 		stock = self.env['stock.picking'].search([('origin','=',self.invoice_origin)])
	# 		if stock:
	# 			lots= []
	# 			for each_rec in stock:
	# 				for each_line in each_rec.move_line_ids_without_package:
	# 					if each_line.product_id==l.product_id:
	# 						# print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
	# 						lots.append(each_line.lot_id)

	# 			if lots:
	# 				return lots
# to get the lot number by panther

class MoveLine(models.Model):
	_inherit = "account.move.line"

	lots_list = fields.Char('Lot Num',compute="lot_num")


	@api.depends('move_id.invoice_origin','product_id')
	def lot_num(self):
		for line in self:
			lot_ref = []
			strip_ref = 0
			ref = 0
			if line.move_id.invoice_origin:
				#split the sale order to fetch the lot ref based on the shipment
				sale_order_ref = line.move_id.invoice_origin
				#match based on the sale order ref
				pickings = self.env['stock.picking'].search([('origin','=',sale_order_ref)])
				for pick in pickings:
					if pick.sale_id:
						move_line = self.env['stock.move.line'].search([('product_id','=',line.product_id.id),('picking_id','=',pick.id)])
						if move_line:
							for move in move_line:
								ref = move.lot_id.name
								if ref:
									print('************',ref)
									lot_ref.append(ref)

			strip_ref =set(lot_ref)
			print(strip_ref,'*****************')
			lots = str(strip_ref).strip("{ }")
			line.lots_list = lots.replace("'"," ")


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# invoice_incoterm_id = fields.Many2one('account.incoterms',string='Incoterms')

	@api.onchange('partner_id')
	def Onchange_incoterm(self):
		for rec in self:
			if rec.partner_id.incoterms:
				rec.incoterm = rec.partner_id.incoterms
			else:
				rec.incoterm = None


# class AccountMove(models.Model):
# 	_inherit = 'account.move'

	