from odoo import api, fields, models,exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import time
import math

from odoo.osv import expression
#from odoo.tools.float_utils import gross_weightfloat_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

class Reason(models.Model):
    _name = "weighment.reason"
    _description = "Weighment Picking"

    name=fields.Char(string="Reason")


class WeighmentPicking(models.Model):
    _name = "weighment.picking"
    _description = "Weighment Picking"
    name = fields.Char(string="Weighment No.",readonly=True)
    weighment_type = fields.Many2one('weighment.picking.type',string="Type",store=True,readonly=True)
    
    shipment_no = fields.Many2one('stock.picking',string="Shipment No.", domain="['&',('state','=','done'),('move_type','=','direct')]")
    date = fields.Datetime(string="Date",default=fields.Datetime.now,readonly=True)
    user_id = fields.Many2one('res.users', string='User', track_visibility='onchange',readonly=True, default=lambda self: self.env.user)
    state = fields.Selection([('draft','Draft'),('open', 'Open'),('release', 'Released'),('close', 'Closed')], string='Status', index=True, default='open')
    
    #for capturing all the product details
    weighment_product_lines = fields.One2many('weighment.product','weigh_product_id')
    #for capturing all the truck details
    weighment_truck_lines = fields.One2many('weighment.truck','weigh_truck_id')
    #for capturing all the trolly details
    weighment_trolly_lines = fields.One2many('weighment.trolly','weigh_trolly_id')
    #for capturing all the trolly details
    weighment_vehicle_lines = fields.One2many('weighment.vehicle','weigh_vehicle_id')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order',domain = "[('gate_sequence','=',gate_in_id)]")

    reason = fields.Many2one('weighment.reason',string='Reason')

    sale_id = fields.Many2one('sale.order', string='Sale Order')

    mo_id = fields.Many2one('mrp.production', string='Manufacturing Order')

    gate_in_id = fields.Many2one('gateentry.inward',string="Gate In Number")
    gate_out_id = fields.Many2one('gateentry.outward',string="Gate Out Number")

    workcenter_id = fields.Many2one('mrp.workcenter',string="Machine Number",domain="[('production_id','=',mo_id)]",related="mo_id.workcenter_id",readonly=True)

    total_products = fields.Float(string="Total Products",default=0.0,compute="compute_total_qty")
    total_truck_weight = fields.Float(string="Total Truck Weight",default=0.0,compute="compute_total_qty")
    empty_truck_weight = fields.Float(string="Empty Truck Weight",default=0.0,compute="compute_total_qty")
    tolerance = fields.Float(string="Tolerance",compute="compute_total_qty")
    gross_weight = fields.Float(string="Total Product Standard Weight",compute="compute_total_qty")
    net_weight = fields.Float(string = 'Net Actual Weight',compute="_total_net_weight")
    difference = fields.Float(string='Difference',compute="_calculate_difference")
    reference = fields.Char(string="Reference")
    deliver_line_id = fields.Many2one('stock.move',string="Stock move")


    @api.depends('weighment_product_lines.product_quantity','weighment_truck_lines.loaded_truck_weight')
    def compute_total_qty(self):
        for line in self:
            total_product_qty = gross_weight = total_truck_weight = empty_truck_weight = tolerance = 0
            for qty in line.weighment_product_lines:
                total_product_qty += qty.product_quantity
                gross_weight += qty.gross_weight

            for tol in line.weighment_product_lines[:1]:
                tolerance += tol.tolerance

            if line.weighment_truck_lines:
                for weight in line.weighment_truck_lines:
                    total_truck_weight += weight.loaded_truck_weight
                    empty_truck_weight += weight.empty_truck_weight
            elif line.weighment_trolly_lines:
                for weight in line.weighment_trolly_lines:
                    total_truck_weight += weight.loaded_trolly_weight
                    empty_truck_weight += weight.empty_trolly_weight
            else:
                for weight in line.weighment_vehicle_lines:
                    total_truck_weight += weight.loaded_vehicle_weight
                    empty_truck_weight += weight.empty_vehicle_weight

            line.update({'total_products': total_product_qty,
                'tolerance':tolerance,
                'gross_weight':gross_weight,
                'total_truck_weight':total_truck_weight,
                'empty_truck_weight':empty_truck_weight})


    @api.depends('total_truck_weight','empty_truck_weight')
    def _total_net_weight(self):
        for order in self:
            order.net_weight = order.total_truck_weight - order.empty_truck_weight



    @api.depends('gross_weight','net_weight')
    def _calculate_difference(self):
        for line in self:
            line.difference = line.net_weight - line.gross_weight



    @api.onchange('purchase_id')
    def _onchange_allowed_purchase_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        result = {}

        # A PO can be selected only if at least one PO line is not already in the invoice
        purchase_line_ids = self.weighment_product_lines.mapped('purchase_line_id')
        purchase_ids = self.weighment_product_lines.mapped('purchase_id').filtered(lambda r: r.order_line <= purchase_line_ids)

        result['domain'] = {'purchase_id': [
            ('state', '=', 'purchase'),'|',('final_display','=',False),'&',
            ('order_completed','=',True),
            ('id', 'not in', purchase_ids.ids),
            ]}
        return result

    # Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            self.purchase_id = self.purchase_id
            return {}
        new_lines = self.env['weighment.product']
        for line in self.purchase_id.order_line - self.weighment_product_lines.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_lines(line)
            new_line = new_lines.new(data)
            new_line._set_additional_po_order_fields(self)
            new_lines += new_line
        self.weighment_product_lines += new_lines
        self.env.context = dict(self.env.context, from_purchase_order_change=True)
        self.purchase_id = False
        self.sale_id = False
        self.mo_id = False
        self.shipment_no = False
        #changing the final_display boolean value to true once the po is used.
        return {}

        
    def _prepare_invoice_line_from_po_lines(self, line):
        invoice_line = self.env['weighment.product']
        data = {
            'purchase_id': line.order_id.id,
            'name': line.order_id.name,
            'product_id': line.product_id.id,
            'po_qty':line.product_qty
        }
        return data

    @api.onchange('weighment_product_lines')
    def _onchange_purchase_order_origin(self):
        purchase_order_ids = self.weighment_product_lines.mapped('purchase_id')
        sale_order_ids = self.weighment_product_lines.mapped('sale_id')
        shiping_order_ids = self.weighment_product_lines.mapped('shipment_no')
        mo_order_ids = self.weighment_product_lines.mapped('mo_id')
        if purchase_order_ids:
            self.reference = ', '.join(purchase_order_ids.mapped('name'))
        if sale_order_ids:
            self.reference = ', '.join(sale_order_ids.mapped('name'))
        if mo_order_ids:
            self.reference = ', '.join(mo_order_ids.mapped('name'))
        if shiping_order_ids:
            self.reference = ', '.join(shiping_order_ids.mapped('name'))
#for shipment 
    @api.onchange('shipment_no')
    def _onchange_allowed_deliver_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        sale orders.
        '''
        result = {}

        # A PO can be selected only if at least one PO line is not already in the invoice
        deliver_line_ids = self.weighment_product_lines.mapped('deliver_line_id')
        deliver_ids = self.weighment_product_lines.mapped('shipment_no').filtered(lambda r: r.move_lines <= deliver_line_ids)
        '''deliver_ids = self.weighment_product_lines.mapped('shipment_no').filtered(lambda r: r.move_lines <= deliver_line_ids)

        result['domain'] = {'shipment_no': [
            ('state', '=', 'sale'),'|',('final_display','=',False),'&',
            ('order_completed','=',True),
            ('id', 'not in', sale_ids.ids),
            ]}'''
        return result

#for sale change

    @api.onchange('sale_id')
    def _onchange_allowed_sale_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        sale orders.
        '''
        result = {}

        # A PO can be selected only if at least one PO line is not already in the invoice
        sale_line_ids = self.weighment_product_lines.mapped('sale_line_id')
        sale_ids = self.weighment_product_lines.mapped('sale_id').filtered(lambda r: r.order_line <= sale_line_ids)

        result['domain'] = {'sale_id': [
            ('state', '=', 'sale'),'|',('final_display','=',False),'&',
            ('order_completed','=',True),
            ('id', 'not in', sale_ids.ids),
            ]}
        return result

    # Load all unsold PO lines
    @api.onchange('sale_id')
    def sale_order_change(self):
        if not self.sale_id:
            self.sale_id = self.sale_id
            return {}

        new_lines = self.env['weighment.product']
        for line in self.sale_id.order_line - self.weighment_product_lines.mapped('sale_line_id'):
            data = self._prepare_invoice_line_from_so_lines(line)
            new_line = new_lines.new(data)
            new_lines += new_line
            new_line._set_additional_po_order_fields(self)

        self.weighment_product_lines += new_lines
        self.env.context = dict(self.env.context, from_sale_order_change=True)
        self.sale_id = False
        self.purchase_id = False
        self.mo_id = False
        self.shipment_no = False
        return {}
    @api.onchange('shipment_no')
    def deliver_order_change(self):
        if not self.shipment_no:
            self.shipment_no = self.shipment_no
            return {}

        new_lines = self.env['weighment.product']
        for line in self.shipment_no.move_lines - self.weighment_product_lines.mapped('deliver_line_id'):
            data = self._prepare_invoice_line_from_deliver_lines(line)
            new_line = new_lines.new(data)
            new_lines += new_line
            new_line._set_additional_po_order_fields(self)

        self.weighment_product_lines += new_lines
        self.env.context = dict(self.env.context, from_sale_order_change=True)
        self.shipment_no = False
        self.purchase_id = False
        self.mo_id = False
        return {}       
    def _prepare_invoice_line_from_so_lines(self, line):
        invoice_line = self.env['weighment.product']
        data = {
            'sale_id': line.order_id.id,
            'name': line.order_id.name+': '+line.name,
            'product_id': line.product_id.id,
            'so_qty':line.product_uom_qty
        }
        return data
    def _prepare_invoice_line_from_deliver_lines(self, line):
        invoice_line = self.env['weighment.product']
        data = {
            'shipment_no': line.picking_id.id,
            'name': line.picking_id.name+': '+line.name,
            'product_id': line.product_id.id,
            'so_qty':line.product_uom_qty,
            'product_quantity':line.quantity_done
        }
        return data#for manufacturing change

    @api.onchange('mo_id')
    def _onchange_allowed_mo_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        mo orders.
        '''
        result = {}

        # A PO can be selected only if at least one PO line is not already in the invoice
        mo_line_ids = self.weighment_product_lines.mapped('mo_id')
        mo_ids = self.weighment_product_lines.mapped('mo_id')

        result['domain'] = {'mo_id': [
            ('state', 'in', ['done','progress']),'|',('final_display','=',False),
            ('order_completed','=',True),
            ]}
        return result
#need to make a mo to appear once when its done
    # Load all unsold PO lines
    @api.onchange('mo_id')
    def mo_order_change(self):
        if not self.mo_id:
            self.mo_id = self.mo_id
            return {}

        new_lines = self.env['weighment.product']
        for line in self.mo_id - self.weighment_product_lines.mapped('mo_id'):
            data = self._prepare_invoice_line_from_mo_lines(line)
            new_line = new_lines.new(data)
            new_lines += new_line
            new_line._set_additional_po_order_fields(self)

        self.weighment_product_lines += new_lines
        self.env.context = dict(self.env.context, from_mo_order_change=True)
        self.mo_id = False
        self.purchase_id = False
        self.sale_id = False
        return {}
        
    def _prepare_invoice_line_from_mo_lines(self, line):
        invoice_line = self.env['weighment.product']
        data = {
            'mo_id': line.id,
            'name': line.name,
            'product_id': line.product_id.id,
            'mo_qty': line.product_qty
        }
        return data




    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('weighment.picking')
        weighment = super(WeighmentPicking, self).create(values)
        return weighment

    
    def button_close(self):
        self.state='close'

    
    
    def button_cancel(self):
        self.state = 'open'
        for lines in self:
            purchase_ids = self.env['purchase.order'].search([('id', '=', self.purchase_id.id)])
            if purchase_ids:
                for line in purchase_ids:
                    if line.order_completed == False:
                        line.update({'final_display':False})
                        #making completed so to not appear once its taken to weighment
        for lines in self:
            sale_ids = self.env['sale.order'].search([('id', '=', self.sale_id.id)])
            if sale_ids:
                for line in sale_ids:
                    if line.order_completed == False:
                        line.update({'final_display':False})
                        #making completed po to not appear once its taken to weighment
        for lines in self:
            mo_ids = self.env['mrp.production'].search([('id', '=', self.mo_id.id)])
            if mo_ids:
                for line in mo_ids:
                    if line.order_completed == False:
                        if line.state == 'done':
                            line.update({'final_display':False})

    
    def calculate_tolerance_limit(self):
        for line in self:
            actual_weight = 0
            difference_weight = 0
            actual_weight = (line.gross_weight) * line.tolerance / 100
            actual_weight_less = -(line.gross_weight) * line.tolerance / 100
            difference_weight = ((line.net_weight) * line.tolerance/100)
            if actual_weight < line.difference:
                raise exceptions.Warning(("Total Weight is above Tolerance limit. Tolerance limit is '%s'. Difference weight is '%s'.") % (actual_weight,line.difference))
            elif actual_weight_less > line.difference:
                raise exceptions.Warning(("Total Weight is below Tolerance limit. Tolerance limit is '%s'. Difference weight is '%s'.") % (actual_weight_less,line.difference))
            else:
                self.state = 'release'
                #making completed po to not appear once its taken to weighment
                for lines in self:
                    purchase_ids = self.env['purchase.order'].search([('id', '=', self.purchase_id.id)])
                    if purchase_ids:
                        for line in purchase_ids:
                            if line.order_completed == False:
                                line.update({'final_display':True})
                #making completed so to not appear once its taken to weighment
                for lines in self:
                    sale_ids = self.env['sale.order'].search([('id', '=', self.sale_id.id)])
                    if sale_ids:
                        for line in sale_ids:
                            if line.order_completed == False:
                                line.update({'final_display':True})
                #making completed po to not appear once its taken to weighment
                for lines in self:
                    mo_ids = self.env['mrp.production'].search([('id', '=', self.mo_id.id)])
                    if mo_ids:
                        for line in mo_ids:
                            if line.order_completed == False:
                                if line.state == 'done':
                                    line.update({'final_display':True})
#adding the truck details

class WeighmentTruckMoves(models.Model):
    _name = "weighment.truck"

    weigh_truck_id = fields.Many2one('weighment.picking',string="Weighment Moves")

    truck_id = fields.Many2one('fleet.vehicle',string="Vehicle No.")
    empty_truck_weight = fields.Integer(string="Empty Truck Weight")
    total_truck_weight = fields.Float(string="Product Weight",store=True,track_visibility="always",compute="_calculate_truck_weight")
    loaded_truck_weight = fields.Float(string="Loaded Truck Weight")
    weighment_type = fields.Many2one('weighment.picking.type',string="Weighment Type", related = "weigh_truck_id.weighment_type",invisible=True)

    @api.depends('loaded_truck_weight','empty_truck_weight')
    def _calculate_truck_weight(self):
        for line in self:
            if line.truck_id:
                line.total_truck_weight = line.loaded_truck_weight - line.empty_truck_weight



class WeighmentTrollyMoves(models.Model):
    _name = "weighment.trolly"

    weigh_trolly_id = fields.Many2one('weighment.picking',string="Weighment")

    trolly_id = fields.Many2one('maintenance.equipment',string="Trolley No.",domain="[('name', 'like', '%TROLLEY%')]")
    empty_trolly_weight = fields.Integer(string="Empty Trolley Weight",related="trolly_id.weight")
    total_trolly_weight = fields.Float(string="Product Weight",store=True,track_visibility="always",compute="_calculate_trolly_weight")
    loaded_trolly_weight = fields.Float(string="Loaded Trolley Weight")
    weighment_type = fields.Many2one('weighment.picking.type',string="Weighment Type", related = "weigh_trolly_id.weighment_type",invisible=True)

    @api.depends('loaded_trolly_weight','empty_trolly_weight')
    def _calculate_trolly_weight(self):
        for line in self:
            if line.trolly_id:
                line.total_trolly_weight = line.loaded_trolly_weight - line.empty_trolly_weight


class WeighmentVehicleMoves(models.Model):
    _name = "weighment.vehicle"

    weigh_vehicle_id = fields.Many2one('weighment.picking',string="Weighment")

    vehicle_id = fields.Char(string="Vehicle No.")
    empty_vehicle_weight = fields.Integer(string="Empty Vehicle Weight")
    total_vehicle_weight = fields.Float(string="Product Weight",store=True,track_visibility="always",compute="_calculate_vehicle_weight")
    loaded_vehicle_weight = fields.Float(string="Loaded Vehicle Weight")
    weighment_type = fields.Many2one('weighment.picking.type',string="Weighment Type", related = "weigh_vehicle_id.weighment_type",invisible=True)

    @api.depends('loaded_vehicle_weight','empty_vehicle_weight')
    def _calculate_vehicle_weight(self):
        for line in self:
            if line.vehicle_id:
                line.total_vehicle_weight = line.loaded_vehicle_weight - line.empty_vehicle_weight


#new class for capturing products
class WeighmentProductMoves(models.Model):
    _name = "weighment.product"

    weigh_product_id = fields.Many2one('weighment.picking',string="Weighment")

    product_id = fields.Many2one('product.product',string="Product")
    name=fields.Char(string="Move name")
    description = fields.Char(string="Description")
    product_uom = fields.Many2one('uom.uom', string='UOM',related="product_id.uom_id",readonly=True)
    product_quantity = fields.Float(string='Quantity', store=True)
    po_qty = fields.Float(string="Purchase order Qty",store=True)
    so_qty = fields.Float(string="Sale order Qty",store=True)
    mo_qty = fields.Float(string="Manufacturing order Qty",store=True)
    product_batch = fields.Char(string='Batch')
    std_weight = fields.Float(string='Standard Weight Per',related="product_id.weight",readonly=True)
    
    gross_weight = fields.Float(string = 'Net Standard Weight',compute="_calculate_gross")
    tolerance = fields.Float(string='Tolerance',related="product_id.tolerance",readonly=True)
    weighment_type = fields.Many2one('weighment.picking.type',string="Weighment Type", related = "weigh_product_id.weighment_type",invisible=True)

    purchase_line_id = fields.Many2one('purchase.order.line',string="Purchase order line")
    purchase_id = fields.Many2one('purchase.order',string="Purchase order")

    sale_line_id = fields.Many2one('sale.order.line',string="Sale order line")
    sale_id = fields.Many2one('sale.order',string="Sale order")

    mo_id = fields.Many2one('mrp.production',string="Manufacturing order")
    deliver_line_id = fields.Many2one('stock.move',string="Stock move")
    shipment_no = fields.Many2one('stock.picking',string="Shipment No.")
#calculating the net standard weight
   
    @api.depends('product_quantity','std_weight')
    def _calculate_gross(self):
        for line in self:
            if line.product_quantity:
                line.gross_weight = line.product_quantity * line.std_weight
            else:
                line.gross_weight = 0.0


    def _set_additional_po_order_fields(self, invoice):
        """ Some modules, such as Purchase, provide a feature to add automatically pre-filled
            invoice lines. However, these modules might not be aware of extra fields which are
            added by extensions of the accounting module.
            This method is intended to be overridden by these extensions, so that any new field can
            easily be auto-filled as well.
            :param invoice : account.invoice corresponding record
            :rtype line : account.invoice.line record
        """
        pass   
#store true quantity_done
class Stock(models.Model):
    _inherit = "stock.move"
    quantity_done = fields.Float('Quantity Done', compute='_quantity_done_compute',store=True, digits=dp.get_precision('Product Unit of Measure'), inverse='_quantity_done_set')