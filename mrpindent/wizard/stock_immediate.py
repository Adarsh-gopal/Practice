from odoo import fields, models, _
from odoo.exceptions import UserError

class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    # def process(self):
    # 	for line in self:
    # 		stockpicking = self.env['stock.picking']
    #         stock = self.env['stock.move.line'].search([('picking_id','=',stockpicking.id)])
    #         var = self.env['indent.order'].search([('name','=',stockpicking.name)])
    #         for rec in var:
    #             for l in stock:
    #                 if l.move_id.product_uom_qty == l.qty_done:
    #                     rec.status = 'Completed'
    #                 if l.move_id.product_uom_qty > l.qty_done:
    #                     rec.status = 'Partially issued'
    #     return super(StockImmediateTransfer, self).process()
