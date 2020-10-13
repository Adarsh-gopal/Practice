# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from num2words import num2words

class salepartner(models.Model):
	_inherit = 'sale.order'

	destination = fields.Char(string='Destination')

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





        
