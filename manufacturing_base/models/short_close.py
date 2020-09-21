# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    planned_to_produce = fields.Float()
    
    def action_short_close(self):

        self.planned_to_produce = self.product_qty

        for line in self.move_raw_ids:
            line.planned_to_consume = line.product_uom_qty



class StockMove(models.Model):
    _inherit = 'stock.move'

    planned_to_consume = fields.Float()



class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    qty_produced = fields.Float()
    balance_qty = fields.Float(compute="_compute_balance")
    # product_qty = fields.Float(required=False)

    @api.depends('product_qty','qty_produced')
    def _compute_balance(self):
        for rec in self:
            rec.balance_qty = rec.product_qty - rec.qty_produced

    @api.model
    def default_get(self, fields):
        res = super(ChangeProductionQty, self).default_get(fields)
        if 'qty_produced' in fields and not res.get('qty_produced') and res.get('mo_id'):
            res['qty_produced'] = self.env['mrp.production'].browse(res['mo_id']).qty_produced
        return res

    def short_close(self):
        for wizard in self:
            production = wizard.mo_id
            production.action_short_close()
            wizard.product_qty = wizard.qty_produced
            print('\n'*3,'quantity to produce',wizard.product_qty,'\n','qantity produced',wizard.qty_produced,'\n'*3)

        self.change_prod_qty()

        return {}