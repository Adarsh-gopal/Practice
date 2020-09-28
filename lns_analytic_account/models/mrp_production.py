# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
import pdb

class MrpProduction(models.Model):
      _inherit = 'mrp.production'

      analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.",store=True,track_visibility='always',readonly=False)
      z_analytic_tag_ids = fields.Many2many('account.analytic.tag','tag_id',string='Analytic Tags')
      z_analytic_tag_ids_default = fields.Many2many('account.analytic.tag','tag_default_id', string='Analytic Tags from Defaults')
      z_analytic_tag_ids_picking_type = fields.Many2many('account.analytic.tag','tag_picking_id',string='Analytic Tags from Operation type')

      
      @api.depends('origin')
      def fetch_analytic_account_id(self):
            # self.ensure_one()
            # if self.origin:
            for line in self:
                  analytic = self.env['sale.order'].search([('name','=',line.z_sale_order_id)])
                  for l in analytic:
                        line.analytic_account_id = l.analytic_account_id.id 
                        analytic_tag_id = self.env['account.analytic.account'].search([('id', '=', line.analytic_account_id.id)])
                        if analytic_tag_id:
                              for tags in analytic_tag_id:
                                    line.z_analytic_tag_ids_default = tags.z_analytic_tag_ids.ids
                                    line.z_analytic_tag_ids_picking_type = line.picking_type_id.z_analytic_tag_ids.ids
                                    line.z_analytic_tag_ids = line.z_analytic_tag_ids_default.ids + line.z_analytic_tag_ids_picking_type.ids

      def _get_finished_move_value(self, product_id, product_uom_qty, product_uom, operation_id=False, byproduct_id=False):
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
            return {
            'product_id': product_id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom,
            'operation_id': operation_id,
            'byproduct_id': byproduct_id,
            'unit_factor': product_uom_qty / self.product_qty,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_finished,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.product_id.with_context(force_company=self.company_id.id).property_stock_production.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'warehouse_id': self.location_dest_id.get_warehouse().id,
            'origin': self.name,
            'group_id': self.procurement_group_id.id,
            'propagate_cancel': self.propagate_cancel,
            'propagate_date': self.propagate_date,
            'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
            'move_dest_ids': [(4, x.id) for x in self.move_dest_ids],
            'analytic_account_id':self.analytic_account_id.id,
            'z_analytic_tag_ids': analytic_tag_ids,
            
            }

      def _generate_raw_move(self, bom_line, line_data):
            quantity = line_data['qty']
            # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
            alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
            if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
                  return self.env['stock.move']
            if bom_line.product_id.type not in ['product', 'consu']:
                  return self.env['stock.move']
            if self.routing_id:
                  routing = self.routing_id
            else:
                  routing = self.bom_id.routing_id
            if routing and routing.location_id:
                  source_location = routing.location_id
            else:
                  source_location = self.location_src_id
            original_quantity = (self.product_qty - self.qty_produced) or 1.0
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
            data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
            'analytic_account_id':self.analytic_account_id.id,
            'z_analytic_tag_ids':analytic_tag_ids,
            }
            return self.env['stock.move'].create(data)

      def _get_raw_move_data(self, bom_line, line_data):
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
            quantity = line_data['qty']
            # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
            alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
            if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
                  return
            if bom_line.product_id.type not in ['product', 'consu']:
                  return
            if self.routing_id:
                  routing = self.routing_id
            else:
                  routing = self.bom_id.routing_id
            if routing and routing.location_id:
                  source_location = routing.location_id
            else:
                  source_location = self.location_src_id
            original_quantity = (self.product_qty - self.qty_produced) or 1.0
            return {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
            'analytic_account_id':self.analytic_account_id.id,
            'z_analytic_tag_ids':analytic_tag_ids,
            }

      
      def post_inventory(self):
            for line in self:
                  for moveline in line.finished_move_line_ids:
                        if moveline.state not in ('done','cancel'):
                              if moveline.lot_id:
                                    moveline.lot_id.z_analytic_tag_ids = moveline.move_id.production_id.z_analytic_tag_ids_default.ids or moveline.production_id.z_analytic_tag_ids_default.ids
            return super(MrpProduction, self).post_inventory()

      
      def button_maintenance_req(self):
            self.ensure_one()
            return {
            'name': _('New Maintenance Request'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'maintenance.request',
            'type': 'ir.actions.act_window',
            'context': {'default_production_id': self.id,
            'default_z_analytic_account': self.analytic_account_id.id,},
            'domain': [('production_id', '=', self.id)],
            }
            super(MrpProduction, self).button_maintenance_req()
            
      def _workorders_create(self, bom, bom_data):
        """
        :param bom: in case of recursive boms: we could create work orders for child
                    BoMs
        """
        workorders = self.env['mrp.workorder']

        # Initial qty producing
        quantity = max(self.product_qty - sum(self.move_finished_ids.filtered(lambda move: move.product_id == self.product_id).mapped('quantity_done')), 0)
        quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom_id)
        if self.product_id.tracking == 'serial':
            quantity = 1.0

        for operation in bom.routing_id.operation_ids:
            workorder = workorders.create({
                'name': operation.name,
                'production_id': self.id,
                'workcenter_id': operation.workcenter_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'z_analytic_id': self.analytic_account_id.id,
                'operation_id': operation.id,
                'state': len(workorders) == 0 and 'ready' or 'pending',
                'qty_producing': quantity,
                'consumption': self.bom_id.consumption,
            })
            if workorders:
                workorders[-1].next_work_order_id = workorder.id
                workorders[-1]._start_nextworkorder()
            workorders += workorder

            moves_raw = self.move_raw_ids.filtered(lambda move: move.operation_id == operation and move.bom_line_id.bom_id.routing_id == bom.routing_id)
            moves_finished = self.move_finished_ids.filtered(lambda move: move.operation_id == operation)

            # - Raw moves from a BoM where a routing was set but no operation was precised should
            #   be consumed at the last workorder of the linked routing.
            # - Raw moves from a BoM where no rounting was set should be consumed at the last
            #   workorder of the main routing.
            if len(workorders) == len(bom.routing_id.operation_ids):
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id and move.bom_line_id.bom_id.routing_id == bom.routing_id)
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.workorder_id and not move.bom_line_id.bom_id.routing_id)

                moves_finished |= self.move_finished_ids.filtered(lambda move: move.product_id != self.product_id and not move.operation_id)

            moves_raw.mapped('move_line_ids').write({'workorder_id': workorder.id})
            (moves_finished | moves_raw).write({'workorder_id': workorder.id})

            workorder._generate_wo_lines()
        return workorders

class Maintenance(models.Model):
      _inherit = 'maintenance.request'

      z_analytic_account = fields.Many2one('account.analytic.account',string="Analytic Account")
