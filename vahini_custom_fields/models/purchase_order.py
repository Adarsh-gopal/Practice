from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    port_of_discharge = fields.Many2one('port.order', string='Port Of Discharge')
    port_of_destination = fields.Many2one('port.order', string='Port Of Destination')
    country_of_origin_goods = fields.Many2one('res.country', string='Country Of Origin Of Goods')
    country_of_final_destination = fields.Many2one('res.country', string='Country Of Final Destination')
    pre_carriage= fields.Selection([
        ('air', 'By Air'),
        ('rail', 'Rail'),
        ('road', 'Road')], string='Pre Carriage')
    carriage= fields.Selection([
        ('sea', 'Sea')], string='Carriage')
    export_shipment_method = fields.Many2one('export.shipment', string='Shipment Method')
    type_of_container = fields.Many2one('type.container', string='Type Of Container')

