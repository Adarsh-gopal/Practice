# -*- coding: utf-8 -*-

from collections import namedtuple
import json
import time

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

class Picking(models.Model):
    _inherit = "stock.picking"

    z_show_supplier = fields.Boolean(compute="_compute_show")

    # @api.multi
    @api.depends('origin')
    def _compute_show(self):
        for line in self:
            if line.purchase_id:
                # if line.origin == self.env['purchase.order'].search([('name','=',self.origin)],limit=1).name:
                line.z_show_supplier = True
            else:
                line.z_show_supplier = False

    # @api.multi
    def button_validate(self):

        if self.purchase_id:
            done_sum = 0
            for move_line in self.move_lines:
                done_sum += move_line.quantity_done
            if done_sum == 0:
                raise UserError(_('Please Enter Done Quantity'))
            for move_line in self.move_lines:
                for po_line in self.purchase_id.order_line:
                    if move_line.product_id.id == po_line.product_id.id and move_line.z_supplier_rate != po_line.price_unit and move_line.quantity_done > 0:
                        raise UserError(_('Purchase Order price and supplier invoice price are not matchaing , kindly revise the PO price .'))
        
        return super(Picking, self).button_validate()