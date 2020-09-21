# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SplitMoWizard(models.TransientModel):
    _name = 'mrp.split.wiz'
    _description = 'Split Manufacturing Order Wizard'

    mo_id = fields.Many2one('mrp.production')
    qty_to_split = fields.Float()

    def split_mo(self):
        new_mo = self.mo_id.copy(default={'product_qty': self.qty_to_split})
        new_mo._onchange_move_raw()
        self.mo_id.product_qty -= self.qty_to_split
        self.mo_id._onchange_move_raw()
        # self.env.cr.execute("""
        #     DELETE FROM stock_move WHERE production_id = %s
        #     """)
        # self.env['stock.move'].search([('production_id','=',self.mo_id.id)]).unlink()
        # print('\n'*3,self.env['stock.move'].search([('production_id','=',self.mo_id.id)]),'\n'*3)
        new_mo.origin_mo = self.mo_id.id



class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    origin_mo = fields.Many2one('mrp.production')
    split_mos = fields.One2many('mrp.production','origin_mo')

    def split_mo(self):
        view = self.env.ref('manufacturing_base.split_mo_wizard_form')
        wiz = self.env['mrp.split.wiz'].create({'mo_id': self.id})
        return{
            'name': _('Split Wizard'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.split.wiz',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }