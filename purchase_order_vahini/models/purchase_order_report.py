from odoo.exceptions import UserError
from odoo import api, fields, models, _
from num2words import num2words

class purchaseorder(models.Model):
	_inherit = 'purchase.order'

	# z_check = fields.Boolean(string='Check',compute='compute_discount')

	# @api.depends('order_line.discount')
	# def compute_discount(self):
	# 	check = False
	# 	for line in self.order_line:
	# 		if line.discount == 0:
	# 			check = True
	# 		if line.discount != 0:
	# 			check = False
	# 	self.z_check = check
	 
	def amt_in_words_po(self, poamount):
		amount1=str(poamount)
		amt= amount1.split(".")
		print(amt[1],amt[0],poamount)
		if int(amt[1]) > 0:
			second_part = ' and '+ num2words(int(amt[1]), lang='en_IN') + ' Paise only '
			print(amt[1],'*****************************************************************')
		else:
			second_part = ' Only '

		return ' Rupees ' + num2words(int(amt[0]), lang='en_IN') + second_part

	def consolidated_quantities(self):
		prods = []
		for line in self.order_line:
			if line.product_id not in [prod['product'] for prod in prods]:
				prods.append({'product':line.product_id,'description':line.name,'hsncode':line.product_id.l10n_in_hsn_code,'taxids':line.calculateigstrate(line.taxes_id),'prodqty':line.product_qty,'price':line.price_unit,'measure':line.product_uom.name,'disc':line.discount,'taxprice':line.price_subtotal/line.product_qty})
		print(prods)
		return prods


	def email_split(self,email):
		esplit=email.split(",")
		if esplit:
			current_name= ''
			for each_email in esplit:
				current_name +=each_email
			if len(current_name) >1:
				name = current_name

		return current_name

class purchase(models.Model):
	_inherit='purchase.order.line'

	def calculaterate(self,tax):
		rate=0
		for tax in self.taxes_id:
			rate = (self.taxes_id.amount/2)
			# print("Tax",rate)

		return rate
		
	def calculateigstrate(self,tax):
		igstrate=0
		cgst_amt=0.0
		for tax in self.taxes_id:
			igstrate = (self.taxes_id.amount)
			# print("Tax",igstrate)

		return igstrate







 
		
 








