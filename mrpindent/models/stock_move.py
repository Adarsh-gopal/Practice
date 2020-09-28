from odoo.tools.float_utils import float_is_zero, float_compare
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import datetime
from datetime import datetime

class StockMove(models.Model):
    _inherit = 'stock.move'

    mrp_indent_stock_line_id = fields.Many2one('indent.order', 'Material Requisition')
    stock_indent_stock_line_id = fields.Many2one('stock.indent.order', 'Material Requisition')
    indent_line_id = fields.Many2one('indent.order.line',
        'Material Requisition Order Line', ondelete='set null', index=True, readonly=True, copy=False)
    stock_indent_line_id = fields.Many2one('stock.indent.order.line',
        'Stock Material Requisition Order Line', ondelete='set null', index=True, readonly=True, copy=False)
    created_indent_line_id = fields.Many2one('indent.order.line',
        'Created Material Requisition Order Line', ondelete='set null', readonly=True, copy=False)
    stock_created_indent_line_id = fields.Many2one('stock.indent.order.line',
        'Created Stock Material Requisition Order Line', ondelete='set null', readonly=True, copy=False)



    


