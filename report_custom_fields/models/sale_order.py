from odoo import models, fields, api, _

class SaleOrder(models.Model):
	_inherit='sale.order'
	advance_amount = fields.Char(string="Advance Amount",store=True)
	payment_method = fields.Many2one('custom.fields',string='Payment Method',store=True ,index=True,ondelete='cascade')
	custom_po_no = fields.Char(string='Custom PO Num', store=True)
	z_delivered_to = fields.Char(string="Deliver To")
	ext_doc_no = fields.Char(string='External Document No', store=True)
	po_date = fields.Date(String='PO Date', store=True)
	order_type = fields.Many2one('sale.order.type',string='Order Type',store=True)
	vehicle = fields.Many2one('fleet.vehicle', domain=[('sale_ok','=',True)], readonly=True, states={'draft': [('readonly', False)]})
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
        ('sea', 'Sea'),
        ('air', 'By Air'),
        ('rail', 'Rail'),
        ('road', 'Road')], string='Carriage')
	export_shipment_method = fields.Many2one('export.shipment', string='Export Shipment Method')
	type_of_container = fields.Many2one('type.container', string='Type Of Container')
	project_name = fields.Char(string="Project Name")
	proforma_sequence = fields.Char(string="Proforma Invoice Number",readonly=True)

	@api.model
	def create(self, vals):
		if vals.get('name', _('New')) == _('New'):
			if 'company_id' in vals:
				vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
				vals['proforma_sequence'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('proforma.sale.order') or _('New')
			else:
				vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
				vals['proforma_sequence'] = self.env['ir.sequence'].next_by_code('proforma.sale.order') or _('New')
		
		# Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
		if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
			partner = self.env['res.partner'].browse(vals.get('partner_id'))
			addr = partner.address_get(['delivery', 'invoice'])
			vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
			vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
			vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
		result = super(SaleOrder, self).create(vals)
		return result



	# def _prepare_invoice(self):
		
	# 	invoice_vals = super(SaleOrder, self)._prepare_invoice()
		

	# 	invoice_vals.update({
	# 		'confirmation_date': self.confirmation_date,
	# 		'z_delivered_to' : self.z_delivered_to,
	# 		'payment_method': self.payment_method.name,
	# 		'order_type': self.order_type.name,
	# 		'ext_doc_no': self.ext_doc_no,
	# 		'custom_po_no': self.custom_po_no,
	# 		'po_date': self.po_date,
	# 		'vehicle': self.vehicle.id,
	# 		'port_of_discharge':self.port_of_discharge.id,
	# 		'port_of_destination':self.port_of_destination.id,
	# 		'country_of_origin_goods':self.country_of_origin_goods.id,
	# 		'country_of_final_destination':self.country_of_final_destination.id,
	# 		'pre_carriage':self.pre_carriage,
	# 		'carriage':self.carriage,
	# 		'export_shipment_method':self.export_shipment_method.id,
	# 		'type_of_container':self.type_of_container.id,
	# 		'proforma_sequence':self.proforma_sequence,
	# 		#'z_cus_biz_type':self.z_cus_biz_type.id,
	# 	})
	# 	return invoice_vals

class SaleOrderType(models.Model):
	_name = "sale.order.type"
	name= fields.Char(store=True ,ondelete='cascade')
	description= fields.Text(string='Description',store=True ,ondelete='cascade')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    l10n_in_hsn = fields.Char('HSN Code', store=True,compute = "_onchange_product_id_hsn")

    @api.depends('product_id')
    def _onchange_product_id_hsn(self):
    	for line in self:
    		line.l10n_in_hsn = "%s" % (line.product_id.l10n_in_hsn_code or "")



class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    

    sale_orders = fields.One2many('sale.order', 'vehicle', string='Sales')