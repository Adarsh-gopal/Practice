import logging
from datetime import date
from odoo import models, api, fields,_
from odoo.exceptions import UserError
import pdb

from odoo.tools.float_utils import float_compare, float_is_zero, float_round
_logger = logging.getLogger(__name__)


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    # Fields for enter the current currency 
    z_currency_rate = fields.Float("BOE Rate",store=True)
    #  Store the converted rate
    z_boe_rate = fields.Float("BOE Rate")




    # @api.onchange('z_currency_rate')
    # def Raise_user_error(self):
    #     if self.z_currency_rate:
    #         raise UserError(_("Please DO NOT add any taxes to this document as it is a imported invoice\n Import duties and other taxes are to be accounted in a separate document."))

    
    @api.onchange('z_currency_rate')
    def boe_rate(self):
        # if the the currency is not equal to the current company currency then only the currency rate is updated
        if self.z_currency_rate > 0 and self.currency_id.id != self.env.user.currency_id.id:
            self.z_boe_rate = 1/self.z_currency_rate
            currency_rate_obj=self.env['res.currency.rate']
            # finding the currency rate for the same cuurency for same date 
            current_currency_id = currency_rate_obj.search([('name','=',self.date),('currency_id','=',self.currency_id.id)
                ,('company_id','=',self.company_id.id)])
            # If the record is found the currence rate is updated else new record id created in Currency rate table.
            if current_currency_id:
                current_currency_id.write({'rate':1/self.z_currency_rate})
            else:
                # Creating the new record in res.currency.rate table.
                currency_rate_obj.create({
                    'name':self.date,
                    'rate':1/self.z_currency_rate,
                    'currency_id':self.currency_id.id,
                    'company_id':self.company_id.id,
                    })

            if self.invoice_line_ids:
                # pdb.set_trace()
                product_purchase_ids= [x.product_id.categ_id.property_stock_account_input_categ_id.id for x in self.invoice_line_ids ]

            # Updating the credit balance in Jurnal Items when the currency is changed in account move
            if  self.line_ids:
                for line in self.line_ids:
                    # pdb.set_trace()
                    if self.partner_id.property_account_payable_id.id == line.account_id.id:
                        line.credit=self.amount_total * self.z_currency_rate
                    elif line.account_id.id in product_purchase_ids:
                        for each_line in self.invoice_line_ids:
                            if each_line.name == line.name:
                                line.debit=each_line.price_subtotal * self.z_currency_rate

            
        # Call the onhange after changeing the currency rate.
        # for line in self.invoice_line_ids:
        #     # pdb.set_trace()
        #     line._onchange_price_subtotal()
        #     line._onchange_mark_recompute_taxes()


    # Overloding thr post methos to restrict the BOE Rate should be > 0
    def action_post(self):
        if self.currency_id.id != 20 and self.z_currency_rate <=0 :
            raise UserError(_("BOE Rate is should be greater than ZERO"))

        if self.mapped('line_ids.payment_id') and any(post_at == 'bank_rec' for post_at in self.mapped('journal_id.post_at')):
            raise UserError(_("A payment journal entry generated in a journal configured to post entries only when payments are reconciled with a bank statement cannot be manually posted. Those will be posted automatically after performing the bank reconciliation."))
        return self.post()





class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    # Fields for enter the current currency 
    z_currency_rate = fields.Float("BOE Rate")
    #  Store the converted rate
    z_boe_rate = fields.Float("BOE Rate")
    z_currency_id = fields.Many2one('res.currency',string='Currency', store=True,compute="get_currency")
    

    # get the currency from PO
    @api.depends('origin')
    def get_currency(self):
        for l in self:
            po_red_id = self.env['purchase.order'].search([('name','=',l.origin)])
            if po_red_id:
                l.z_currency_id = po_red_id.currency_id.id
            else :
                l.z_currency_id  = False


    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

        # Propose to use the sms mechanism the first time a delivery
        # picking is validated. Whatever the user's decision (use it or not),
        # the method button_validate is called again (except if it's cancel),
        # so the checks are made twice in that case, but the flow is not broken
        sms_confirmation = self._check_sms_confirmation_popup()
        if sms_confirmation:
            return sms_confirmation

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # pdb.set_trace()
        if self.z_currency_rate <= 0 and  self.z_currency_id.id != 20 and self.picking_type_id.code == 'incoming':
            # pdb.set_trace()
            raise UserError(_("BOE Rate is should be greater than ZERO"))
        elif  self.picking_type_id.code == 'incoming' and self.z_currency_id.id != 20 and self.z_currency_rate > 0:
            self.z_boe_rate = 1/self.z_currency_rate
            # pdb.set_trace()
            currency_rate_obj=self.env['res.currency.rate']
            # finding the currency rate for the same cuurency for same date 
            current_currency_id = currency_rate_obj.search([('name','=',date.today()),('currency_id','=',self.z_currency_id.id)
                ,('company_id','=',self.company_id.id)])
            # If the record is found the currence rate is updated else new record id created in Currency rate table.
            if current_currency_id:
                _logger.info("This is my debug message ! @@@@@@@@@@@@@@@@@Currency Record is updated in@@@@@@@@@@@@@@",current_currency_id.name  )
                _logger.error("This is my debug message ! @@@@@@@@@@@@@@@@@Currency Record is updated in@@@@@@@@@@@@@@%s'",current_currency_id.name  )
                # _logger.debug("This is my debug message ! @@@@@@@@@@@@@@@@@Currency Record is updated in@@@@@@@@@@@@@@" ,current_currency_id.name)
                # print("@@@@@@@@@@@@@@@@@Currency Record is updated in@@@@@@@@@@@@@@" ,current_currency_id.name)
                current_currency_id.write({'rate':1/self.z_currency_rate})
            else:
                # Creating the new record in res.currency.rate table.
                _logger.info("################Currency Record is created in#################" ,current_currency_id.name  )
                _logger.error("################Currency Record is created in#################'%s'",current_currency_id.name  )
                # _logger.debug("################Currency Record is created in#################" ,current_currency_id.name)
                # print("################Currency Record is created in#################" ,current_currency_id.name)
                currency_rate_obj.create({
                    'name':date.today(),
                    'rate':1/self.z_currency_rate,
                    'currency_id':self.purchase_id.currency_id.id,
                    'company_id': self.company_id.id})

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        return





    # # Overiding the  Valodate button in Tranfers screen for update the currency rate in res.currency.rate table.
    # def button_validate(self):
    #     res=super(StockPickingInherit, self).button_validate()
    #     _logger.info("111111111111111111111111111111",self.z_currency_rate  )
    #     _logger.error("ERRRRRRRRRRRRRRRRRRRRRRR...:%s',",self.z_currency_rate  )
    #     if self.z_currency_rate <= 0 and  self.z_currency_id.id != 20 and self.picking_type_id.code == 'incoming':
    #         raise UserError(_("BOE Rate is should be greater than ZERO"))
    #     elif  self.picking_type_id.code == 'incoming' and self.z_currency_id.id != 20 and self.z_currency_rate > 0:
    #         self.z_boe_rate = 1/self.z_currency_rate
    #         currency_rate_obj=self.env['res.currency.rate']
    #         # finding the currency rate for the same cuurency for same date 
    #         current_currency_id = currency_rate_obj.search([('name','=',date.today()),('currency_id','=',self.z_currency_id.id)
    #             ,('company_id','=',self.company_id.id)])
    #         # If the record is found the currence rate is updated else new record id created in Currency rate table.
    #         if current_currency_id:
    #             _logger.info("This is my debug message ! @@@@@@@@@@@@@@@@@Currency Record is updated in@@@@@@@@@@@@@@",current_currency_id.name  )
    #             _logger.error("This is my debug message ! @@@@@@@@@@@@@@@@@Currency Record is updated in@@@@@@@@@@@@@@%s'",current_currency_id.name  )
    #             # _logger.debug("This is my debug message ! @@@@@@@@@@@@@@@@@Currency Record is updated in@@@@@@@@@@@@@@" ,current_currency_id.name)
    #             # print("@@@@@@@@@@@@@@@@@Currency Record is updated in@@@@@@@@@@@@@@" ,current_currency_id.name)
    #             current_currency_id.write({'rate':1/self.z_currency_rate})
    #         else:
    #             # Creating the new record in res.currency.rate table.
    #             _logger.info("################Currency Record is created in#################" ,current_currency_id.name  )
    #             _logger.error("################Currency Record is created in#################'%s'",current_currency_id.name  )
    #             # _logger.debug("################Currency Record is created in#################" ,current_currency_id.name)
    #             # print("################Currency Record is created in#################" ,current_currency_id.name)
    #             currency_rate_obj.create({
    #                 'name':date.today(),
    #                 'rate':1/self.z_currency_rate,
    #                 'currency_id':self.purchase_id.currency_id.id,
    #                 'company_id': self.company_id.id})
    #     return 


        

class res_currency(models.Model):
    _inherit = "res.currency"

    inverse_rate = fields.Float(
        'Current Inverse Rate', digits=(12, 4),
        help='The rate of the currency from the currency of rate 1 (0 if no '
                'rate defined).'
    )

    # @api.one
    @api.onchange('rate')
    def get_inverse_rate(self):
        self.inverse_rate = self.rate and (
            1.0 / (self.rate))


    rate = fields.Float(compute='_compute_current_rate', string='Current Rate', digits=(12, 12),
                        help='The rate of the currency to the currency of rate 1.')


    # @api.multi
    @api.depends('rate_ids.rate')
    def _compute_current_rate(self):
        for each_rate in self:
            date = self._context.get('date') or fields.Datetime.now()
            # company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
            company_id = self._context.get('company_id')
            # the subquery selects the last rate before 'date' for the given currency/company
            query = """SELECT c.id, (SELECT r.rate FROM res_currency_rate r
                                      WHERE r.currency_id = c.id AND r.name <= %s
                                        AND (r.company_id IS NULL OR r.company_id = %s)
                                   ORDER BY r.company_id, r.name DESC
                                      LIMIT 1) AS rate
                       FROM res_currency c
                       WHERE c.id IN %s"""
            self._cr.execute(query, (date, company_id, tuple(each_rate.ids)))
            currency_rates = dict(self._cr.fetchall())
            for currency in each_rate:
                currency.rate = currency_rates.get(currency.id) or 1.0

class res_currency_rate(models.Model):
    _inherit = "res.currency.rate"
    rate = fields.Float(string='Current Rate', digits=(12, 12),)

    inverse_rate = fields.Float(
        'Inverse Rate', digits=(12, 4),
        compute='get_inverse_rate',
        inverse='set_inverse_rate',
        help='The rate of the currency from the currency of rate 1',
    )

    # @api.one
    @api.depends('rate')
    def get_inverse_rate(self):
        for l in self:
            l.inverse_rate = l.rate and (1.0 / (l.rate))

    # @api.one
    def set_inverse_rate(self):
        for k in self:
            k.rate = k.inverse_rate and (1.0 / (k.inverse_rate))





class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    _description = 'Immediate Transfer'

   

    def process(self):
        # pdb.set_trace()
        pick_to_backorder = self.env['stock.picking']
        pick_to_do = self.env['stock.picking']
        for picking in self.pick_ids:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                # for move_line in move.move_line_ids:
                #     move_line.qty_done = move_line.product_uom_qty
                raise UserError(_("Please Enter the product Quantity ")) 
            if picking._check_backorder():
                pick_to_backorder |= picking
                continue
            pick_to_do |= picking
        # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
        if pick_to_do:
            pick_to_do.action_done()
        if pick_to_backorder:
            return pick_to_backorder.action_generate_backorder_wizard()
        return False






    



    