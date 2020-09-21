"""

"""
from odoo import models, fields, api,_
from datetime import datetime
import pdb

class InventoryBaseReport(models.Model):

	_name = 'inventory.base.report'
	_description='inventory.base.report'

	product_id = fields.Many2one('product.product', string="Product")
	move_id = fields.Many2one('stock.move', string="Move")
	uom_id = fields.Many2one('uom.uom', string="Uom")
	category_id = fields.Many2one('product.category', string="Category")
	warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse')
	location_id = fields.Many2one('stock.location',string='Source')
	location_dest_id = fields.Many2one('stock.location',string='Destnation')
	company_id = fields.Many2one('res.company',string='Company')
	valuation_id = fields.Many2one('stock.valuation.layer',string='Valuation')
	product_code = fields.Char("Internal Reference")
	date=fields.Datetime(string="Date")
	name = fields.Char("Name")
	product_qty=fields.Float("Qty")
	price_unit=fields.Float("Price")
	value=fields.Float("Value")

	# Purchase retun 
	# Sales shipment 
	# Negative adjustiment 
	# Tranfer shipment 
	# Consumpution



	transaction_types = fields.Selection([
        ('p_receipt', 'Purchase Receipt'),
        ('p_return', 'Purchase Return'),
        ('positive', 'Positive Adjustment'),
        ('negative', 'Negative Adjustment'),
        ('s_shipment', 'Sales Shipment'),
        ('s_return', 'Sales Returns'),
        ('in', 'Consumpution'),
        ('out', 'Output'),
        ('t_shipment', 'Transfer Shipment'),
        ('t_receipt', 'Transfer Receipt'),
        ('internal', 'Internal Moment'),
        ], string='Transaction Type')

class StockQuant(models.Model):
    _inherit = 'stock.quant'


    warehouse_id = fields.Many2one('stock.warehouse', store=True,compute='get_warehouse')



    @api.depends('product_id','location_id')
    def get_warehouse(self):
    	for each in self:
    		if each.location_id:
	    		curr_id =each.location_id.parent_path.split("/")
	    		if curr_id[0]:

	    			loca_id=self.env['stock.location'].search([('id','=',curr_id[1])])
	    			ware_id=self.env['stock.warehouse'].search([('code','=',loca_id.name)])
	    			each.warehouse_id = ware_id.id
	    		else:
	    			each.warehouse_id= False
	    	else:
	    		each.warehouse_id= False


class ProductProduct(models.Model):
	_inherit = 'product.product'

	def _change_standard_price(self, new_price, counterpart_account_id=False):
		InventoryObj = self.env['inventory.base.report']
		company_id = self.env.company
		for product in self:
			if product.cost_method not in ('standard', 'average'):
				continue
			quantity_svl = product.sudo().quantity_svl
			if float_is_zero(quantity_svl, precision_rounding=product.uom_id.rounding):
				continue
			diff = new_price - product.standard_price
			value = company_id.currency_id.round(quantity_svl * diff)
			if company_id.currency_id.is_zero(value):
				continue
			prod_query='''select sq.product_id ,sum(sq.quantity) as tot_qty


			from 
			stock_quant sq,stock_location sl 
			where 
			sq.product_id =%s and
			sq.location_id= sl.id and
			sl.usage ='internal'

			group by sq.product_id'''

			ware_quer='''

			select sq.product_id ,sum(sq.quantity) qty,sq.warehouse_id

			from 
			stock_quant sq,stock_location sl 
			where 
			sq.product_id =%s and
			sq.location_id= sl.id and
			sl.usage ='internal'

			group by sq.product_id,sq.warehouse_id'''

			po_params = (product.id,)
			self.env.cr.execute(prod_query,po_params)
			po_qty_result = self.env.cr.dictfetchall()
			tot_qty_ve=0.0
			if po_qty_result:
				tot_qty_ve= po_qty_result[0]['tot_qty']


			wa_params = (product.id,)
			self.env.cr.execute(ware_quer,wa_params)
			wo_result = self.env.cr.dictfetchall()
			for each_line in wo_result:
				currrent_value_ve = value/tot_qty_ve

				vlas_list={
				'product_id':self.id,
				'uom_id':self.uom_id.id,
				'category_id': self.categ_id.id,
				'product_code': self.default_code,
				'warehouse_id':  each_line['warehouse_id'],
				'product_qty':  0,
				'price_unit':   new_price,
				'location_id': False,
				'location_dest_id': False,
				'transaction_types': False,
				'date': datetime.today(),
				'value':   currrent_value_ve *each_line['qty'],
				'company_id':company_id.id,
				'move_id':False

				}
				# pdb.set_trace()
				new_id =InventoryObj.create(vlas_list)
		res = super(ProductProduct, self)._change_standard_price(new_price, counterpart_account_id)





class ProductCategory1(models.Model):
	_inherit = 'product.category'



	def write(self, vals):
		
		res = super(ProductCategory1, self).write(vals)
		Product = self.env['product.product']
		InventoryObj = self.env['inventory.base.report']
		if 'property_cost_method' in vals or 'property_valuation' in vals:
			# When the cost method or the valuation are changed on a product category, we empty
			# out and replenish the stock for each impacted products.
			new_cost_method = vals.get('property_cost_method')
			new_valuation = vals.get('property_valuation')
			impacted_categories_1 ={}
			move_vals_list = []

			for product_category in self:
				
				# Empty out the stock with the current cost method.
				if new_cost_method:
					description = _("Costing method change for product category %s: from %s to %s.") \
					% (self.display_name, self.property_cost_method, new_cost_method)
				else:
					description = _("Valuation method change for product category %s: from %s to %s.") \
					% (self.display_name, self.property_valuation, new_valuation)
				out_svl_vals_list, products_orig_quantity_svl, products = Product\
				._svl_empty_stock(description, product_category=product_category)

				
				impacted_categories_1[product_category] = (products, description, products_orig_quantity_svl)
				for product_category, (products, description, products_orig_quantity_svl) in impacted_categories_1.items():
					# Replenish the stock with the new cost method.
					in_svl_vals_list = products._svl_replenish_stock(description, products_orig_quantity_svl)

				prod_query='''select sq.product_id ,sum(sq.quantity) as tot_qty


					from 
					stock_quant sq,stock_location sl 
					where 
					sq.product_id =%s and
					sq.location_id= sl.id and
					sl.usage ='internal'

					group by sq.product_id'''

				ware_quer='''

					select sq.product_id ,sum(sq.quantity) qty,sq.warehouse_id

					from 
					stock_quant sq,stock_location sl 
					where 
					sq.product_id =%s and
					sq.location_id= sl.id and
					sl.usage ='internal'

					group by sq.product_id,sq.warehouse_id'''
				# Creating Negative records
				for each_line in out_svl_vals_list:


					product_rec = Product.search([('id','=',each_line['product_id'])])
					
					po_params = (product_rec.id,)
					self.env.cr.execute(prod_query,po_params)
					po_qty_result = self.env.cr.dictfetchall()
					tot_qty_ve=0.0
					if po_qty_result:
						tot_qty_ve= po_qty_result[0]['tot_qty']

					# pdb.set_trace()
					wa_params = (product_rec.id,)
					self.env.cr.execute(ware_quer,wa_params)
					wo_result = self.env.cr.dictfetchall()
					currrent_value_ve = each_line['value']/tot_qty_ve
					for each in wo_result:
						print("out_svl_vals_listout_svl_vals_list",currrent_value_ve *each['qty'])

						# quant_ids = self.env['stock.quant'].search([('product_id','=',product_rec.id),('location_id.usage','=', 'internal')])
						vlas_list={
						'product_id':product_rec.id,
						'uom_id':product_rec.uom_id.id,
						'category_id': product_rec.categ_id.id,
						'product_code': product_rec.default_code,
						'warehouse_id':  each['warehouse_id'],
						'product_qty':  0.0,
						'price_unit':   0.0,
						'location_id': False,
						'location_dest_id': False,
						'transaction_types': False,
						'date': datetime.today(),
						'value':   currrent_value_ve *each['qty'],
						'company_id':each_line['company_id'],
						'move_id':False

						}
						# location_id.usage','=', 'internal
						new_id =InventoryObj.create(vlas_list)

				# Creating Positive records
				for each_product in in_svl_vals_list:

					product_rec = Product.search([('id','=',each_product['product_id'])])
					positive_params = (product_rec.id,)
					self.env.cr.execute(prod_query,positive_params)
					positive_result = self.env.cr.dictfetchall()
					positive_tot_qty=0.0
					if positive_result:
						positive_tot_qty= po_qty_result[0]['tot_qty']

					# pdb.set_trace()

					wa_params = (product_rec.id,)
					self.env.cr.execute(ware_quer,wa_params)
					po_wo_result = self.env.cr.dictfetchall()
					currrent_value = each_product['value']/positive_tot_qty

					for line in po_wo_result:
						print("out_svl_vals_listout_svl_vals_list",currrent_value *line['qty'])
						vlas_list1={
						'product_id':product_rec.id,
						'uom_id':product_rec.uom_id.id,
						'category_id': product_rec.categ_id.id,
						'product_code': product_rec.default_code,
						'warehouse_id':  line['warehouse_id'],
						'product_qty':  0.0,
						'price_unit':   0.0,
						'location_id': False,
						'location_dest_id': False,
						'transaction_types': False,
						'date': datetime.today(),
						'value':   currrent_value * line['qty'],
						'company_id':each_product['company_id'],
						'move_id':False

						}
						new_id =InventoryObj.create(vlas_list1)






class StockQuant(models.Model):

	_inherit = 'stock.move'
	# z_price = fields.Float(compute='compute_product_price',store=True)
	data_sent = fields.Boolean(default=False,compute='compute_inventory_value',store=True)

	s_type = fields.Selection([
        ('supplier', 'Vendor Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('production', 'Production'),
        ('transit', 'Transit Location')], string='Source Location Type',
        compute='compute_s_location_type',store=True)
	d_type = fields.Selection([
        ('supplier', 'Vendor Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('production', 'Production'),
        ('transit', 'Transit Location')], string='Destnation Location Type',
        compute='compute_s_location_type',store=True)

	z_price = fields.Float(compute='compute_product_price',store=True)


	@api.depends('state','picking_id.state')
	def compute_product_price(self):
		for rec in self:
			if rec.state == 'done' and rec.picking_id.state == 'done':
				rec.z_price = rec.product_id.standard_price
			else:
				rec.z_price = False


	@api.depends('location_id','location_dest_id')
	def compute_s_location_type(self):
		for l in self:
			if l.location_id and l.location_dest_id:
				l.s_type =l.location_id.usage
				l.d_type =l.location_dest_id.usage
			else:
				l.s_type= False
				l.d_type= False




	@api.depends('state','picking_id.state')
	def compute_inventory_value(self):
		for rec in self:
			if rec.state == 'done':
				InventoryObj = self.env['inventory.base.report']
				ValuationObj = self.env['stock.valuation.layer']
				valuation_query ='''select 
					sum(unit_cost) as unit,
					sum(quantity) as qty,
					sum(value) as va
				from  stock_valuation_layer
				 where stock_move_id = %s and 
				   stock_landed_cost_id is null and 
				   quantity != 0.0 and
					product_id = %s'''
				params = (rec.id,rec.product_id.id)

				self.env.cr.execute(valuation_query, params)
				result = self.env.cr.dictfetchall() 
				if rec.s_type == 'inventory':
					curr_transaction = 'positive'
				elif rec.d_type == 'inventory':
					curr_transaction ='negative'
				elif rec.s_type == 'supplier':
					curr_transaction ='p_receipt'
				elif rec.d_type =='supplier':
					curr_transaction ='p_return'
				elif rec.s_type == 'customer':
					curr_transaction ='s_return'
				elif rec.d_type =='customer':
					curr_transaction ='s_shipment'
				elif rec.s_type == 'production' and rec.location_id.is_transit  == False:
					curr_transaction ='out'
				elif rec.d_type =='production' and rec.location_dest_id.is_transit == False:
					curr_transaction ='in'
				elif rec.s_type == 'production' and rec.location_id.is_transit ==True:
					curr_transaction ='t_receipt'
				elif rec.d_type =='production' and rec.location_dest_id.is_transit==True:
					curr_transaction ='t_shipment'
				elif rec.d_type == rec.s_type :
					curr_transaction = 'internal'
				else :
					curr_transaction = False

				# If the valuation is not thery we have to cosider the move
				if result[0]['va'] != None:
					curr_qty =result[0]['qty'] 
					if curr_qty ==0:
						price= 0.0
						qty= 0.0
					else:
						price= result[0]['unit']
						print("price= result[0]['unit']price= result[0]['unit']price= result[0]['unit']price= result[0]['unit']", result[0],result[0]['unit'])
						qty= curr_qty
				else:
					price= 0.0
					qty= rec.product_uom_qty

				if rec.s_type =="internal" :
					w_code = rec.location_id.complete_name.split('/')[0]

					warehouse_id = self.env['stock.warehouse'].search([('code','=',w_code)])
				elif rec.s_type =="internal" and rec.d_type =="internal":
					w_code = rec.location_dest_id.complete_name.split('/')[0]
					warehouse_id = self.env['stock.warehouse'].search([('code','=',w_code)])
				else:
					w_code = rec.location_dest_id.complete_name.split('/')[0]
					warehouse_id = self.env['stock.warehouse'].search([('code','=',w_code)])
				if curr_transaction in ['t_shipment','in']:
					qty =  -(abs(qty))


				vlas_list={
					'product_id':rec.product_id.id,
					'uom_id':rec.product_uom.id,
					'category_id': rec.product_id.categ_id.id,
					'product_code': rec.product_id.default_code,
					'warehouse_id':  warehouse_id.id if warehouse_id else False,
					'product_qty':  qty,
					'price_unit': price,
					'location_id': rec.location_id.id,
					'location_dest_id': rec.location_dest_id.id,
					'transaction_types': curr_transaction,
					'date': rec.date,
					'value': qty*price,
					'move_id':rec.id,
					'company_id':rec.company_id.id


				}
				new_id =InventoryObj.create(vlas_list)
			else:
				rec.data_sent=False



class StockValuationLayer22(models.Model):


	_inherit = 'stock.valuation.layer'

	data_sent = fields.Boolean(default=False,compute='compute_inventory_value',store=True)

	@api.depends('stock_move_id')
	def compute_inventory_value(self):
		for l in self:
			InventoryObj = self.env['inventory.base.report']
			ValuationObj = self.env['stock.valuation.layer']
			if l.stock_landed_cost_id :

				# query ='''select 

				# 	ABS(sum(quantity)) as qty,
				# 	ABS(sum(value)) as va
				# from  stock_valuation_layer
				#  where stock_move_id = %s and 
				#  		stock_landed_cost_id is null and
				# 		product_id = %s'''

				# params = (l.stock_move_id.id,l.product_id.id)

				# self.env.cr.execute(query, params)
				# result = self.env.cr.dictfetchall() 

				# # valuvation_ids =ValuationObj.search([('stock_move_id','=',l.stock_move_id.id),('product_id','=',l.product_id.id),('remaining_value','=',True)])
				# curr_id = InventoryObj.search([('company_id','=',l.company_id.id),('move_id','=',l.stock_move_id.id)],limit=1)
				# if l.create_date.date() == l.stock_move_id.date.date():

				# 	curr_id.write({	
				# 					'value' : result[0]['va'],
				# 					'price_unit' : result[0]['va']/result[0]['qty'],
				# 					'valuation_id':l.id
				# 					})
				# else :
				rec=l.stock_move_id
				vlas_list={
				'product_id':rec.product_id.id,
				'uom_id':rec.product_uom.id,
				'category_id': rec.product_id.categ_id.id,
				'product_code': rec.product_id.default_code,
				'warehouse_id':  rec.picking_id.picking_type_id.warehouse_id.id if rec.id else False,
				'product_qty':  0.0,
				'price_unit': 0.0,
				'location_id': rec.location_id.id,
				'location_dest_id': rec.location_dest_id.id,
				'transaction_types': 'p_receipt',
				'date': l.create_date,
				'value': l.value,
				'company_id':rec.company_id.id,
				'move_id':rec.id,
				'valuation_id':l.id,

				}
				new_id =InventoryObj.create(vlas_list)
				l.write({'data_sent': True})
			# else :
			# 	vlas_list={
			# 		'product_id':l.product_id.id,
			# 		'uom_id':l.product_id.uom_id.id,
			# 		'category_id': l.product_id.categ_id.id,
			# 		'product_code': l.product_id.default_code,
			# 		'warehouse_id':  False,
			# 		'product_qty':  0.0,
			# 		'price_unit': 0.0,
			# 		'location_id': False,
			# 		'location_dest_id': False,
			# 		'transaction_types': False,
			# 		'date': l.create_date,
			# 		'value': l.value,
			# 		'company_id':l.company_id.id,
			# 		'move_id':False,
			# 		'valuation_id':l.id

			# 		}
			# 	new_id =InventoryObj.create(vlas_list)

























