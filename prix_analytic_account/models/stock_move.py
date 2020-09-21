# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero, pycompat
import pdb
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.")
    z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.",store=True,track_visibility='always',compute='check_analytic_account')
    z_disp_fetch_button = fields.Boolean(string="Display Fetch Button")
    z_disp_fetch_tags = fields.Boolean(string="Display Tags",default=True)

    
    @api.depends('sale_id')
    def _compute_move_analytic_tags(self):
        for line in self:
            if line.sale_id:
                line.z_disp_fetch_button = True
            else:
                line.z_disp_fetch_button = False

    
    @api.depends('purchase_id','sale_id')
    def check_analytic_account(self):
        for line in self:
            if line.purchase_id:
                line.z_analytic_account_id = line.purchase_id.z_account_analytic_id.id
            elif line.sale_id:
                line.z_analytic_account_id = line.sale_id.analytic_account_id.id
            elif line.sale_id:
                line.z_analytic_account_id = False
            
    
    # @api.onchange('analytic_account_id')
    # def onchange_product_id_analytic_tags_shipment(self):
    #     for lines in self:
    #         for line in lines.move_ids_without_package:
    #             if not lines.sale_id:
    #                 rec = self.env['account.analytic.account'].search([('id', '=', lines.analytic_account_id.id)])
    #                 line.z_analytic_tag_ids = False
    #                 line.z_analytic_tag_ids = rec.z_analytic_tag_ids.ids

    
    def button_validate(self):
        if not self.z_analytic_account_id:
            raise UserError(_('Kindly select the Analytic Account before validating this Transfer'))
            # var = self.env['sale.order'].search([('id','=',self.sale_id.id)])
            # for l in self:
            #     l.commitment_date = self.date_done
        # pdb.set_trace()
        # if self.move_ids_without_package:
        #     for line in self.move_ids_without_package:
        #         line.analytic_account_id = self.z_analytic_account_id
        
        return super(StockPicking, self).button_validate()

    def action_done(self):
        s = super(StockPicking,self).action_done()
        var = self.env['sale.order'].search([('id','=',self.sale_id.id)])
        for l in var:
            l.write({'commitment_date': self.date_done})
        return s


    #this function works fine if detailed operation is enabled
    #but its not good manual selection of analytical tags which does not have sale id.
    '''@api.onchange('move_line_ids_without_package')
    def change_analytical_tagss(self):
        for picking in self:
            for move in picking.move_ids_without_package:
                for line in picking.move_line_ids_without_package:
                    if move.product_id.id == line.product_id.id:
                        move.z_analytic_tag_ids = line.z_analytic_tag_ids.ids'''

    # def change_analytical_tags(self):
    #     for move in self.move_ids_without_package:
    #         stock_line = self.env['stock.move.line'].search([('picking_id', '=', move.picking_id.id)])
    #         if stock_line:
    #             for line in stock_line:
    #                 for lines in stock_line:
    #                     if move.product_id.id == line.product_id.id:
    #                         if line.z_analytic_tag_ids != lines.z_analytic_tag_ids:
    #                             raise UserError(_('Analytic tag mismatched'))
    #                         else:
    #                             move.z_analytic_tag_ids = line.z_analytic_tag_ids.ids
    #                             self.z_disp_fetch_tags = False


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.",store=True)

    #moving value from stock inventory line
    z_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    z_num = fields.Char(string="Check")


    @api.depends('product_id')
    def get_account(self):
        for l in self:
            for line in l.picking_id:
                if line:
                    l.analytic_account_id = line.z_analytic_account_id.id





    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        if move_lines:
            # pdb.set_trace()
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            if self.picking_id:
                #value being passed from stock picking/ transfers to journal entries
                new_account_move = AccountMove.sudo().create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': description,
                    'stock_move_id': self.id,
                    'z_analytic_account_id':self.picking_id.z_analytic_account_id.id,
                    'stock_valuation_layer_ids': [(6, None, [svl_id])],
                    'type': 'entry',
                })
                new_account_move.post()
            else:
                #value being passed from stock inventory to journal entries
                new_account_move = AccountMove.sudo().create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': description,
                    'stock_move_id': self.id,
                    'z_analytic_account_id':self.analytic_account_id.id,
                    'stock_valuation_layer_ids': [(6, None, [svl_id])],
                    'type': 'entry',
                })
                new_account_move.post()

    #stock_account
    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        debit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
        }

        credit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }

        rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    z_analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags')


    # @api.depends('lot_id')
    # def compute_analytical_tags(self):
    #     for lines in self:
    #         if lines.picking_id.sale_id:
    #             if lines.lot_id:
    #                 lines.z_analytic_tag_ids = lines.lot_id.z_analytic_tag_ids.ids
    #         if lines.picking_id.sale_id:
    #             stock_line = self.env['stock.move.line'].search([('product_id', '=', lines.product_id.id)])
    #             if stock_line:
    #                 for line in stock_line:
    #                     if line.production_id:
    #                         if line.product_id.id == lines.product_id.id:
    #                             if lines.lot_id:
    #                                 if line.lot_id.id == lines.lot_id.id:
    #                                     lines.z_analytic_tag_ids = line.production_id.z_analytic_tag_ids_default.ids
                                        


