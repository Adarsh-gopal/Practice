from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning
import pdb

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contain_qty = fields.Float('Contained Qty', default=1.0)
    z_package = fields.Integer('PKG',default=1)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True,compute='compute_z_package')
    unit_price = fields.Float('Order Price Unit', digits='Product Price', default=0.0,readonly=False,compute='compute_price_units')

    @api.onchange('product_packaging')
    def Onchange_contained_qty(self):
        for l in self:
            l.contain_qty = l.product_packaging.qty

    @api.depends('product_packaging')
    def compute_z_package(self):
        for l in self:
            l.product_uom_qty = l.contain_qty * l.z_package

    @api.onchange('z_package')
    def Onchange_z_package(self):
        for l in self:
            l.product_uom_qty = l.contain_qty * l.z_package

    @api.depends('product_uom_qty')
    def compute_price_units(self):
        self.unit_price = 0
        for l in self:
            l.unit_price = l.product_uom_qty * l.price_unit

    @api.onchange('product_uom_qty')
    def Onchange_qty(self):
        for l in self:
            if l.product_packaging:
                # pdb.set_trace()
                # if l.product_uom_qty % l.contain_qty != 0:
                #     raise Warning(_("Product Uom Qty should be Multiple of Contained Quantity(%s)") % (l.contain_qty))
                l.z_package = (l.product_uom_qty / l.contain_qty)

    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        return {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
            'product_packaging': self.product_packaging
        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    z_package = fields.Integer('PKG',compute='_compute_package',store=True)
    product_packaging = fields.Many2one('product.packaging')

    @api.depends('product_packaging','quantity')
    def _compute_package(self):
        for rec in self:
            # if rec.quantity % (rec.product_packaging.qty or 1) != 0:
            #     raise Warning(_("Product Uom Qty should be Multiple of Contained Quantity(%s)") % (rec.product_packaging.qty))
            rec.z_package = rec.quantity / (rec.product_packaging.qty or 1)