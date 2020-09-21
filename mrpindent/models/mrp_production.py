from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import datetime
from datetime import datetime

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    indent_state = fields.Selection(
            [('draft', 'Draft'),
             ('indent_created', 'Material Requisition Created'),
             ('waiting_approval', 'Waiting for Approval'),
             ('done', 'Material Requisition Approved'),
             ('cancel', 'Material Requisition Canceled'),
             ('reject', 'Material Requisition Rejected')], string='Material Requisition Status', readonly=True, copy=False, default='draft')
    mrp_indent_order_count = fields.Integer(string='# of Material Requisition Orders', compute='_indent_count')
    # z_sale_order_id = fields.Char(string='Sale Order Reference',store=True,track_visibility='always',compute="_check_saleorder")

    # @api.depends('origin')
    # def _check_saleorder(self):
    #     for line in self:
    #         var = self.env['mrp.production'].search([('origin','like','SO')])
    #         for l in var: 
    #             line.z_sale_order_id = l.origin
    #         variabl = self.env['mrp.production'].search([('origin','=',line.name)])
    #         for rec in variabl:
    #             if line.z_sale_order_id:
    #                 line.z_sale_order_id = rec.z_sale_order_id

    
    # def post_inventory(self):
    #     for order in self:
    #         # for line in order.finished_move_line_ids:
    #         #     if line.z_operator == False:
    #         #         line.update({
    #         #         'z_operator': line.move_id.production_id.logger_name
    #         #         })
    #         moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
    #         moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
    #         for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
    #             move.product_uom_qty = move.quantity_done
    #         moves_to_do._action_done()
    #         moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
    #         order._cal_price(moves_to_do)
    #         moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done','cancel'))
    #         moves_to_finish._action_done()
    #         #order.action_assign()
    #         consume_move_lines = moves_to_do.mapped('move_line_ids')
    #         for moveline in moves_to_finish.mapped('move_line_ids'):
    #             if moveline.product_id == order.product_id and moveline.move_id.has_tracking != 'none':
    #                 if any([not ml.lot_produced_id for ml in consume_move_lines]):
    #                     raise UserError(_('You can not consume without telling for which lot you consumed it'))
    #                 # Link all movelines in the consumed with same lot_produced_id false or the correct lot_produced_id
    #                 filtered_lines = consume_move_lines.filtered(lambda x: x.lot_produced_id == moveline.lot_id)
    #                 moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
    #             else:
    #                 # Link with everything
    #                 moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})
    #     return True

    
    def _indent_count(self):
        for order in self:
            indent_count = self.env['mrp.indent'].search([('origin', '=', order.id)])
            order.mrp_indent_order_count = len(indent_count)

    
    def button_indent_create(self):
        indent_count = self.env['indent.order']
        if not indent_count:
            self.indent_state = 'indent_created'
            vals = {
                'origin': self.id,
                'require_date': self.date_planned_start,
                'company_id': self.company_id.id,
                'picking_type_id': self.picking_type_id.id,
                #'z_analytic_account_id':self.analytic_account_id.id,
                'location_dest_id': self.production_location_id.id,

            }
            indent_obj = self.env['indent.order'].create(vals)
            move_lines_obj = self.env['indent.order.line']
            for line in self.move_raw_ids:
                if line.reserved_availability < line.product_uom_qty:
                    qty = line.product_uom_qty - line.reserved_availability
                    move_line = {}
                    move_line = {
                                'product_id': line.product_id.id,
                                'product_uom_qty': qty,
                                'product_uom_qty_reserved': line.reserved_availability,
                                'product_uom': line.product_id.uom_id.id,
                                # 'location_id': line.product_id.property_stock_production.id,
                                # 'location_dest_id': line.product_id.property_stock_inventory.id,
                                'mrp_indent_product_line_id': indent_obj.id
                                }
                    move_lines_obj.create(move_line)
        else:
            if self.indent_state == 'indent_created':
                raise UserError(_("Material Requisition already created, Please Check and Confirm your Material Requisition"))
            else:
                raise UserError(_("Material Requisition already created, Please wait for the store team approval"))

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    z_operator = fields.Char(string="Operator Name")
    