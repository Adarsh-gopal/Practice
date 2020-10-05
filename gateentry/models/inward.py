from odoo import models, fields, api, _,exceptions

class Inward(models.Model):
	_name = 'gateentry.inward'

	name = fields.Char(string='Inward Number',required=True, readonly= True,copy=False, default=lambda self: _('New'))
	state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], required=True, default='draft')
	location_code = fields.Many2one('gateentry.warehouse',string="Warehouse",required=True,domain="[('current_user', '=', current_user)]")
	station_form = fields.Char(string='Station From',required=True)
	doc_time = fields.Datetime('Document Date and Time',required=True)
	description = fields.Char(string='Description')
	post_time = fields.Datetime('Posting Date and Time',readonly=True)
	lr_number = fields.Char("LR/RR No.")
	lr_date = fields.Date("LR/RR Date")
	vehicle_number = fields.Char("Vehicle Number")
	entry_type = fields.Selection([('returnable', 'Returnable'), ('non_returnable', 'Non Returnable')],default='returnable', required=True)
	company_vehicle_number = fields.Many2one('fleet.vehicle')
	odometer_value = fields.Float(string="Odometer Value")
	current_user = fields.Many2one('res.users','User',default=lambda self: self.env.user,readonly=True)
	comments = fields.Text("Comments")
	item_description = fields.Char(string='Item Description')

	sales_return_order_ids = fields.One2many('sale.return.order.inward','sales_return_order_id')
	purchase_order_ids = fields.One2many('purchase.order.inward','purchase_order_id')
	internal_transfer_ids = fields.One2many('internal.transfer.inward','internal_transfer_order_id')
	driver_name = fields.Many2one('hr.employee',domain="[('job_id.name', '=', 'DRIVER')]")
	cleaner_name = fields.Many2one('hr.employee',domain="[('job_id.name', '=', 'CLEANER')]")
	z_status = fields.Char(string="Status")
	z_gate_out = fields.Datetime(string="Gate Out Date and Time")
	image_variant = fields.Binary(
    	"Customer Image",store=True, attachment=True,
    	help="This field holds the image used as image for the product variant, limited to 1024x1024px.")

	def gate_out_button(self):
		self.z_status = "Gate Out"
		self.z_gate_out = fields.Datetime.now()

	def update_purchase(self):
		for line in self.purchase_order_ids:
			var = self.env['purchase.order'].search([('id', '=', line.purchase_source_no.id)])
			for ln in var:
				ln.update({'gate_sequence':line.purchase_order_id.id})

				
	@api.model
	def create(self, vals):
		#on save create a sequence and changing the state
		vals['name'] = self.env['ir.sequence'].next_by_code('gateentry.inward')
		rec = super(Inward, self).create(vals)
		rec.state = 'done'
		rec.post_time = fields.Datetime.now()
		for line in rec.company_vehicle_number.log_contracts:
			if line.cost_subtype_id.z_gate_validate == True:
				if line.state == 'expired':
					raise models.ValidationError(("'%s' Contract has been expired for Vehicle '%s'" )%(line.cost_subtype_id.name,line.vehicle_id.name))
		if rec.company_vehicle_number:
			vals = {
			'vehicle_id': rec.company_vehicle_number.id,
			'value':rec.odometer_value,
			}
			vehicle_obj = self.env['fleet.vehicle.odometer'].create(vals)
		return rec
		return super(Inward,self).create(vals)

	@api.constrains('doc_time')
	def _check_release_date(self):
		for r in self:
			#Restricting the date selection
			if r.doc_time > fields.Datetime.now():
				raise models.ValidationError('Document date must be in the past')

class sales_challan_items(models.Model):
	_name = 'sale.return.order.inward'
	sales_return_order_id = fields.Many2one('gateentry.inward')
	name = fields.Char(string='Challan Number',required=True)
	challan_date = fields.Date("Challan Date",required=True)
	description = fields.Char(string='Description')
	source_no = fields.Many2one('stock.picking',string="Source Number",domain="[('gate_entry_attach_inward','=', False),'&',('location_id','=', 9),'&',('state','=', 'assigned'),('picking_type_id','=', 1)]")
	#source_no = fields.Many2one('stock.picking',string="Source Number",domain="[('name', 'like', '%WH/IN%'),'&',('state', '=', 'assigned'),('origin','like','%Return of WH/OUT/%')]")
	source_name = fields.Char(string="Source Name")
	so_name = fields.Many2one('sale.order',string="Sale order")
	reference = fields.Many2one('stock.picking',string="Reference")
	z_vehicle_no = fields.Many2one('fleet.vehicle',string="Vehicle No",related="source_no.z_vehicle_no",readonly=True)
	z_driver = fields.Many2one('hr.employee',string="Driver",related="source_no.z_driver",readonly=True)
	z_cleaner = fields.Many2one('hr.employee',string="Cleaner",related="source_no.z_cleaner",readonly=True)

	@api.onchange('source_no')
	def _onchange_partner_sale_return(self):
		for line in self:
			line.source_name = line.source_no.partner_id.name
			line.so_name = line.source_no.sale_id.id

class purchase_challan_items(models.Model):
	_name = 'purchase.order.inward'
	purchase_order_id = fields.Many2one('gateentry.inward')
	purchase_name = fields.Char(string='Challan Number',required=True)
	purchase_challan_date = fields.Date("Challan Date",required=True)
	purchase_description = fields.Char(string='Description')
	purchase_source_no = fields.Many2one('purchase.order',string="Source Number",domain="[('state','=','purchase')]")
	purchase_source_name = fields.Char(string="Source Name")
	@api.onchange('purchase_source_no')
	def _onchange_partner_purchase_inward(self):
		for line in self:
			line.purchase_source_name = line.purchase_source_no.partner_id.name

class internal_challan_items(models.Model):
	_name = 'internal.transfer.inward'
	internal_transfer_order_id = fields.Many2one('gateentry.inward')
	internal_transfer_name = fields.Char(string='Challan Number',required=True)
	internal_transfer_challan_date = fields.Date("Challan Date",required=True)
	internal_transfer_description = fields.Char(string='Description')
	internal_transfer_source_no = fields.Many2one('internal.transfer.outward',string="Source Number")
	internal_transfer_source_name = fields.Char(string="Source Name")

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	gate_sequence = fields.Many2one('gateentry.inward',string="gate sequence",store = True)

