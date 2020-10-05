from odoo import api, fields, models, tools, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    quantity_alt_uom = fields.Char('Quantity Alt Uom')
    conversion = fields.Float('Conversion')
    alternate_uom = fields.Many2one('uom.uom',string="Alternate UOM")
    alternate_uom_update = fields.Char("Alternate UOM Update")
    z_package = fields.Many2one('uom.uom',"Package UOM")
    z_package_ratio = fields.Integer(string="Package Quantity")

    @api.onchange('alternate_uom')
    def alternate_uom_change(self):
        self.alternate_uom_update = self.alternate_uom.name

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    quantity_alt_uom = fields.Float('Quantity in Alt. UOM', compute='_set_total')
    product_id = fields.Many2one(
        'product.product', 'Product',
        ondelete='restrict', readonly=True, required=True)
    product_tmpl_id = fields.Many2one(
        'product.template', string='Product Template',
        related='product_id.product_tmpl_id')
    conversion_prod = fields.Float('Conversion Prod',store=True,readonly=True,related="product_tmpl_id.conversion")
    alternate_uom = fields.Char('Alternate UOM',store=True,readonly=True,related="product_tmpl_id.alternate_uom_update")

    @api.onchange('quantity','conversion_prod')
    def _set_total(self):
        for line in self:
        	line.quantity_alt_uom = float(line.quantity) * float(line.conversion_prod)


