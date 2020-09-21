# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from num2words import num2words

class salepartner(models.Model):
	_inherit = 'sale.order'

	destination = fields.Char(string='Destination')

	def print_sfdyes_quotation(self):
		return self.env.ref('sf_dyes_quotation.custom_quotation_sfdyes').report_action(self)

	def print_sfdyes_promo_quotation(self):
		return self.env.ref('sf_dyes_quotation.custom_proforma_sfdyes').report_action(self)

	@api.onchange('partner_id')
	def Onchange_destination(self):
		for l in self:
			l.destination = l.partner_id.city

	def amt_in_words(self, amount):
		amount1=str(amount)
		amt= amount1.split(".")
		if int(amt[1]) > 0:
			second_part = ' Rupees and '+ num2words(int(amt[1]), lang='en_IN').capitalize() + ' Paise only '
		else:
			second_part = ' Rupees Only '

		return num2words(int(amt[0]), lang='en_IN').capitalize() + " " +second_part





        
