from odoo import api, fields, models,exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

class outward(models.Model):
	_name = 'gateentry.outward'

	name = fields.Char(string='Outward Number',required=True, readonly= True,copy=False, default=lambda self: _('New'))
	state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], required=True, default='draft')
	location_code = fields.Many2one('gateentry.warehouse',string="Warehouse",required=True,domain="[('current_user', '=', current_user)]")
	station_form = fields.Char(string='Station To',required=True)
	doc_time = fields.Datetime('Document Date and Time',required=True)
	description = fields.Char(string='Description')
	post_time = fields.Datetime('Posting Date and Time', readonly=True)
	lr_number = fields.Char("LR/RR No.")
	lr_date = fields.Date("LR/RR Date")
	vehicle_number = fields.Char("Vehicle Number")
	entry_type = fields.Selection([('returnable', 'Returnable'), ('non_returnable', 'Non Returnable')],default='returnable', required=True)
	company_vehicle_number = fields.Many2one('fleet.vehicle')
	odometer_value = fields.Float(string="Odometer Value")
	current_user = fields.Many2one('res.users','User',default=lambda self: self.env.user,required=True)
	comments = fields.Text("Comments")
	item_description = fields.Char(string='Item Description')

	sale_order_outward_ids = fields.One2many('sale.order.outward','sale_order_outward_id')
	purchase_return_order_outward_ids = fields.One2many('purchase.return.order.outward','purchase_return_order_outward_id')
	internal_transfer_outward_ids = fields.One2many('internal.transfer.outward','internal_transfer_order_outward_id')
	driver_name = fields.Many2one('hr.employee',domain="[('job_id.name', '=', 'DRIVER')]")
	cleaner_name = fields.Many2one('hr.employee',domain="[('job_id.name', '=', 'CLEANER')]")
	image_variant = fields.Binary(
    	"Customer Image",store=True, attachment=True,
    	help="This field holds the image used as image for the product variant, limited to 1024x1024px.")

	@api.model
	def create(self, vals):
		#on save create a sequence and changing the state
		vals['name'] = self.env['ir.sequence'].next_by_code('gateentry.outward')
		rec = super(outward, self).create(vals)
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
		return super(outward,self).create(vals)

	@api.constrains('doc_time')
	def _check_release_date(self):
		for r in self:
			#Restricting the date selection
			if r.doc_time > fields.Datetime.now():
				raise models.ValidationError('Document date must be in the past')


class outward_sales_challan_items(models.Model):
	_name = 'sale.order.outward'
	sale_order_outward_id = fields.Many2one('gateentry.outward')
	invoice_check = fields.Char(string='Invoice Function',compute="compute_invoice_ref")
	name = fields.Char(string='Reference')
	challan_date = fields.Date("Challan Date")
	description = fields.Char(string='Description')
	source_no = fields.Many2one('stock.picking',string="Source Number",domain="[('gate_entry_attach_outward', '=', False),'&',('location_dest_id', '=', 9),'&',('state', '=', 'done'),('picking_type_id', '=', 2)]")
	#source_no = fields.Many2one('sale.order',string="Source Number",domain="[('gate_entry_attach_outward', '=', False),'&',('location_dest_id', '=', 9),'&',('state', '=', 'assigned'),('picking_type_id', '=', 2)]")
	source_name = fields.Char(string="Source Name")
	z_vehicle_no = fields.Many2one('fleet.vehicle',string="Vehicle No",related="source_no.z_vehicle_no")
	z_driver = fields.Many2one('hr.employee',string="Driver",related="source_no.z_driver")
	z_cleaner = fields.Many2one('hr.employee',string="Cleaner",related="source_no.z_cleaner")
	
	@api.onchange('source_no')
	def _onchange_partner_sale_outward(self):
		for line in self:
			line.source_name = "%s" % (line.source_no.partner_id.name or "")

	
	@api.depends('sale_order_outward_id.company_vehicle_number','sale_order_outward_id','sale_order_outward_id.vehicle_number')
	def compute_invoice_ref(self):
		invoice_merge = 0
		invoice_origin = 0
		invoice_op = 0
		for line in self:
			if line.sale_order_outward_id.company_vehicle_number:
				for invoice in self.env['account.move'].search([('vehicle', '=', line.sale_order_outward_id.company_vehicle_number.id),('state','!=','draft')]):
					if invoice.weighment_status == False:
						invoice_origin = invoice.number
						line.challan_date = invoice.date_invoice
						invoice_merge = str(invoice_origin)+ ', ' +str(invoice_merge)
						line.name = invoice_merge.strip(", 0")
			else:
				if line.sale_order_outward_id.vehicle_number:
					for invoice in self.env['account.move'].search([('ext_vehicle_no', '=', str(line.sale_order_outward_id.vehicle_number)),('state','!=','draft')]):
						if invoice.weighment_status == False:
							invoice_origin = invoice.number
							line.challan_date = invoice.date_invoice
							invoice_merge = str(invoice_origin)+ ', ' +str(invoice_merge)
							line.name = invoice_merge.strip(", 0")

		for lines in self:
			if lines.name:
				invoice_order = lines.name.split(", ")
				for io in invoice_order:
					for inv in self.env['account.move'].search([('number', '=', io)]):
						inv.write({'weighment_status':True})

class outward_purchase_challan_items(models.Model):
	_name = 'purchase.return.order.outward'
	purchase_return_order_outward_id = fields.Many2one('gateentry.outward')
	purchase_name = fields.Char(string='Challan Number',required=True)
	purchase_challan_date = fields.Date("Challan Date",required=True)
	purchase_description = fields.Char(string='Description')
	purchase_source_no = fields.Many2one('stock.picking',string="Source Number",domain="[('gate_entry_attach_outward', '=', False),'&',('location_dest_id', '=', 8),'&',('state', '=', 'done'),('picking_type_id', '=', 2)]")
	#purchase_source_no = fields.Many2one('stock.picking',string="Source Number",domain="[('name', 'like', '%WH/OUT%'),'&',('state', '=', 'assigned'),('origin','like','%Return of WH/IN/%')]")
	purchase_source_name = fields.Char(string="Source Name")
	po_name = fields.Many2one('purchase.order',string="Purchase order")
	reference = fields.Many2one('stock.picking',string="Reference")

	
	@api.onchange('purchase_source_no')
	def _onchange_partner_purchase_return(self):
		for line in self:
			line.purchase_source_name = line.purchase_source_no.partner_id.name
			line.po_name = line.purchase_source_no.purchase_id.id

class outward_internal_challan_items(models.Model):
	_name = 'internal.transfer.outward'
	internal_transfer_order_outward_id = fields.Many2one('gateentry.outward')
	internal_transfer_name = fields.Char(string='Challan Number',required=True)
	internal_transfer_challan_date = fields.Date("Challan Date",required=True)
	internal_transfer_description = fields.Char(string='Description')
	name = fields.Many2one('stock.picking',string="Source Number",domain="[('gate_entry_attach_outward', '=', False),'&',('location_dest_id', '=', 8),'&',('state', '=', 'done'),('picking_type_id', '=', 2)]")
	internal_transfer_source_name = fields.Char(string="Source Name")
	
	@api.onchange('name')
	def _onchange_partner_internal_outward(self):
		for line in self:
			line.internal_transfer_source_name = "%s" % (line.name.partner_id.name or "")

