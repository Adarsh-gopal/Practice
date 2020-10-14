

from itertools import groupby
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    delivery_origin = fields.Text(string="Delivery Origin",compute="display_delivery")

    @api.depends('invoice_line_ids.quantity')
    def display_delivery(self):
    	delivery_merge = 0
    	delivery_origin =0
    	for line in self:
            if line.invoice_origin:
                sale_order = line.invoice_origin.split(", ")
                for delivery in self.env['stock.picking'].search([('sale_id.name', '=', sale_order)]):
                    if delivery.name:
                        delivery_origin = delivery.name
                        delivery_merge = str(delivery_origin)+ ', '+ str(delivery_merge)
                    line.delivery_origin = delivery_merge.strip(", 0")
            else:
                line.delivery_origin = False