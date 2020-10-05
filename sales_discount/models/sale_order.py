
import uuid

from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools.misc import formatLang

from odoo.addons import decimal_precision as dp
import pdb


class SaleOrder(models.Model):
    _inherit = "sale.order"
    discount_line_ids = fields.One2many('sale.discount.lines', 'sale_discount_id', string='Discount Lines', copy=True, auto_join=True)

    amount_dis = fields.Monetary(string='Amount Prod Dis', store=True, readonly=True, compute='_amount_all_dis')
    trade_dis = fields.Monetary(string='Trade Discount', store=True, readonly=True, compute='_amount_all_dis')
    quantity_dis = fields.Monetary(string='Quantity Discount', store=True, readonly=True, compute='_amount_all_dis')
    special_dis = fields.Monetary(string='Special Discount', store=True, readonly=True, compute='_amount_all_dis') 
    amount_untaxed = fields.Monetary(string='Sales TTO', store=True, readonly=True, compute='_amount_all', track_visibility='onchange') 
    gross_sales = fields.Monetary(string='Gross Sales', store=True, readonly=True,compute='_amount_all') 
    cal_done = fields.Boolean(string="Calculation Done",default=False)
    round_off_value = fields.Monetary(store=True,compute='_amount_all_dis', string='Round off amount')
    rounded_total = fields.Monetary(store=True,compute='_amount_all_dis', string='Net Total')
    round_active = fields.Boolean(string="Round Active",default=True)
    amount_total = fields.Monetary(string='Gross Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    amount_tax = fields.Monetary(string='Total Tax', store=True, readonly=True, compute='_amount_all')
    confirmation_date = fields.Datetime(string='Confirmation Date')

    order_lines = fields.Char(string="Required Field for sale order category discount")
    sale_order_line = fields.Boolean('Sale Discount Line',store=True)
    visibility_button = fields.Boolean('Visibility of Buttons',store=True)
    #z_fiscal_bool = fields.Boolean(string="Fiscal Value Filter",store=True,compute="func_fiscal_position")

    # @api.depends('order_line.category_ids')
    # def sale_order_line_discount(self):
    #     self.sale_order_line = False
    #     for l in self.order_line:
    #         if l.category_ids:
    #             self.sale_order_line = True
    #             if self.sale_order_line == True:
    #                 self.onchange_discount_values()

    
    def action_confirm(self):
        for line in self:
            if self.cal_done == False:
                raise models.ValidationError('First calculate the discounts and then confirm the Sale order...!!!')
        return super(SaleOrder,self).action_confirm()

    # 
    # def _prepare_invoice(self):
    #     """
    #     Prepare the dict of values to create the new invoice for a sales order. This method may be
    #     overridden to implement custom invoice generation (making sure to call super() to establish
    #     a clean extension chain).
    #     """
    #     self.ensure_one()
    #     journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
    #     if not journal_id:
    #         raise UserError(_('Please define an accounting sales journal for this company.'))
    #     invoice_vals = {
    #         'name': self.client_order_ref or '',
    #         'origin': self.name,
    #         'type': 'out_invoice',
    #         'account_id': self.partner_invoice_id.property_account_receivable_id.id,
    #         'partner_id': self.partner_invoice_id.id,
    #         'partner_shipping_id': self.partner_shipping_id.id,
    #         'journal_id': journal_id,
    #         'currency_id': self.pricelist_id.currency_id.id,
    #         'comment': self.note,
    #         'payment_term_id': self.payment_term_id.id,
    #         'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
    #         'company_id': self.company_id.id,
    #         'user_id': self.user_id and self.user_id.id,
    #         'team_id': self.team_id.id,
    #     }
    #     return invoice_vals


    # @api.depends('partner_invoice_id','warehouse_id','fiscal_position_id','partner_id')
    # def func_fiscal_position(self):
    #     for line in self:
    #         if line.warehouse_id.partner_id.state_id.code != line.partner_invoice_id.state_id.code:
    #             line.fiscal_position_id = 1
    #         else:
    #             line.fiscal_position_id = False


    
    @api.onchange('discount_line_ids')
    def change_discount_values(self):
        for line in self.discount_line_ids:
            line.sale_discount_id.cal_done = False
        for line in self.order_line:
            if line.trade_amount or line.quantity_amount or line.special_amount:
                line.trade_discount = line.quantity_discount = line.special_discount = 0
                line.trade_amount = line.quantity_amount = line.special_amount = 0

    
    # @api.onchange('order_line.product_id')
    # def change_weight_base_price(self):
    #     for line in self:
    #         if line.order_type.name != 'PROJECT ORDER':
    #             for lines in line.order_line:
    #                 lines.weight = 0
    #                 lines.base_price = 0
    #                 lines.dis_price_unit = lines.product_id.lst_price
    #                 lines.price_unit = lines.dis_price_unit

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            order.update({
                        'amount_untaxed': False,
                        'amount_tax': False,
                        'amount_total': False,
                        #gross sales is the sum of price unit * quantity
                        'gross_sales': False
                    })
            for l in order.pricelist_id.company_id.currency_id:
                amount_untaxed = amount_tax = amount_dis = gross_sales = 0.0
                for line in order.order_line:
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
                    gross_sales += line.gross_total
                order.update({
                    'amount_untaxed': l.round(amount_untaxed),
                    'amount_tax': l.round(amount_tax),
                    'amount_total': amount_untaxed + amount_tax,
                    #gross sales is the sum of price unit * quantity
                    'gross_sales': l.round(gross_sales)
                })
    

    

    # @api.depends('order_line.trade_amount','order_line.quantity_amount','order_line.special_amount','order_line.price_total','amount_untaxed','amount_tax')
    # def _amount_all(self):
    #     """
    #     Compute the total amounts of the SO.
    #     """
    #     for order in self:
    #         amount_untaxed = amount_tax = amount_dis = gross_sales = 0.0
    #         amount_trade = amount_qty = amount_spcl = 0.0
    #         amt = 0.0
    #         var = 0.0
    #         for line in order.order_line:
    #             amount_trade += line.trade_amount
    #             amount_qty += line.quantity_amount
    #             amount_spcl += line.special_amount
    #             if order.trade_dis or order.quantity_dis or order.special_dis:
    #                 amount_untaxed += line.price_subtotal
    #                 amount_tax += line.price_tax
    #                 gross_sales += line.gross_total
    #                 var = (amount_untaxed)-(amount_trade + amount_qty + amount_spcl)
    #                 amt = var + amount_tax
    #                 # print(amount_untaxed , var,amount_tax,amount_trade,amount_qty,amount_spcl,'&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&7')
    #                 # print((amount_trade + amount_qty + amount_spcl),'tttttttttttttttttttttttttttttttttttttt')
    #             else:
    #                 amount_untaxed += line.price_subtotal
    #                 amount_tax += line.price_tax
    #                 gross_sales += line.gross_total
    #         if order.trade_dis or order.quantity_dis or order.special_dis:
    #             order.update({
    #                 'amount_untaxed': (amount_untaxed) - (amount_trade + amount_qty + amount_spcl),#order.pricelist_id.currency_id.round(amount_untaxed),
    #                 'amount_tax': amount_tax,#order.pricelist_id.currency_id.round(amount_tax),
    #                 'amount_total': amt,
    #                 #gross sales is the sum of price unit * quantity
    #                 'gross_sales': gross_sales#order.pricelist_id.currency_id.round(gross_sales)
    #             })
    #         else:
    #             order.update({
    #                 'amount_untaxed': amount_untaxed,#order.pricelist_id.currency_id.round(amount_untaxed),
    #                 'amount_tax': amount_tax,#order.pricelist_id.currency_id.round(amount_tax),
    #                 'amount_total': amount_untaxed + amount_tax,
    #                 #gross sales is the sum of price unit * quantity
    #                 'gross_sales': gross_sales#order.pricelist_id.currency_id.round(gross_sales)
    #                 })

    @api.depends('order_line.trade_amount','order_line.quantity_amount','order_line.special_amount','amount_untaxed','amount_tax')
    def _amount_all_dis(self):
        """
        Compute the total amounts of the Discount Line and display in Sales order main form.
        """
        for order in self:
            amount_trade = amount_qty = amount_spcl = 0.0
            amount_untaxed = amount_tax = amount_dis = gross_sales = 0.0
            amt = 0.0
            var = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_trade += line.trade_amount
                amount_qty += line.quantity_amount
                amount_spcl += line.special_amount
                var = (amount_untaxed)-(amount_trade + amount_qty + amount_spcl)
                amt = var + amount_tax
            order.update({
                'amount_dis': amount_trade + amount_qty + amount_spcl,
                #adding different type of discounts individually
                'trade_dis':-amount_trade,
                'quantity_dis':-amount_qty,
                'special_dis':-amount_spcl,
            })
            order.rounded_total = round(order.amount_untaxed + order.amount_tax)
            order.round_off_value = order.rounded_total - (order.amount_untaxed + order.amount_tax)



    #Merge different categories assigned to products and sumup their subtotal in new tab created as Discount
    # @api.depends('order_type')
    # def _onchange_order_line(self):
    #     #this function is automatically trigerred
    #     for lines in self:
    #         pdb.set_trace()
    #         if lines.order_type:
    #             categ_grouped = 0
    #             categ_lines = 0
    #             categ_grouped = lines.get_product_discount_values()
    #             categ_lines = lines.discount_line_ids.filtered('manual')
    #             for line in categ_grouped.values():
    #                 categ_lines += categ_lines.new(line)
    #             lines.discount_line_ids = categ_lines
    #             for line in lines.order_line:
    #                 line.trade_amount = line.quantity_amount = line.special_amount = 0.0
    #                 line.trade_discount = line.quantity_discount = line.special_discount = 0.0
    #                 line.order_id.cal_done = False
    #         else:
    #             lines.order_lines = False
    #     return

#Combining the categories to group and moving them to discount tab

    def push_categories(self):
        for l in self:
            l.visibility_button = True
            categ_grouped = 0
            categ_lines = 0
            categ_grouped = l.get_product_discount_values()
            categ_lines = l.discount_line_ids.filtered('manual')
            for lines in categ_grouped.values():
                categ_lines += categ_lines.new(lines)
            l.discount_line_ids = categ_lines
            for line in l.order_line:
                line.trade_amount = line.quantity_amount = line.special_amount = 0.0
                line.trade_discount = line.quantity_discount = line.special_discount = 0.0
                line.order_id.cal_done = False


                # var = 0
                # rec = 0
                # if line.product_id.item_category == line.category_ids:
                #     var += line.category_ids.id
                #     rec += line.gross_total
                #     print(var,rec,'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                #     l.discount_line_ids = [(0,0,{
                #         'category':var,
                #         'amount':rec,
                #         'sale_discount_id':self.id,
                #         }
                #         )]

    
    def get_product_discount_values(self):
        categ_grouped = {}
        for line in self.order_line:
            if not line.mtrs: 
                price_unit = line.dis_price_unit * (1 - (line.discount or 0.0) / 100.0)
                categ = line.category_ids.compute_all_prod_discount(price_unit, self.currency_id, line.product_uom_qty, line.product_id, self.partner_id)['categ']
                for categ_line in categ:
                    val = self._prepare_categ_line_vals(line, categ_line)
                    key = self.env['item.category'].browse(categ_line['id']).get_grouping_key_categ(val)

                    if key not in categ_grouped:
                        categ_grouped[key] = val
                    else:
                        categ_grouped[key]['amount'] += val['amount']
            else:
                price_unit = line.dis_price_unit * (1 - (line.discount or 0.0) / 100.0)
                categ = line.category_ids.compute_all_prod_discount(price_unit, self.currency_id, line.mtrs, line.product_id, self.partner_id)['categ']
                for categ_line in categ:
                    val = self._prepare_categ_line_vals(line, categ_line)
                    key = self.env['item.category'].browse(categ_line['id']).get_grouping_key_categ(val)
                    if key not in categ_grouped:
                        categ_grouped[key] = val
                    else:
                        categ_grouped[key]['amount'] += val['amount']
        return categ_grouped
    
    def _prepare_categ_line_vals(self, line, categ_line):
        vals = {

            'sale_discount_id': self.id,
            'category': categ_line['id'],
            'trade_discount_id':3,
            'special_discount_id':2,
            'quantity_discount_id':1,
            'sequence': categ_line['sequence'],
            'manual': False,
            'amount': categ_line['amount'],
    
        }

        return vals

#adding the total value of discount to the sale order line and the calculation is made on each line.
#This function is triggered on click of button
    def merge_product_discount(self):
        for order in self.order_line:
            for categ in self.discount_line_ids:
                order.order_id.cal_done=False
                if order.order_id.cal_done == False:
                    if not order.mtrs:
                        if order.category_ids.id == categ.category.id:
                            order.order_id.cal_done = True
                            order.update({
                                'trade_discount':categ.trade_discounts,
                                'trade_amount':((order.price_unit*order.product_uom_qty)*categ.trade_discounts)/100,
                                'quantity_discount':categ.quantity_discount,
                                'quantity_amount':((order.price_unit*order.product_uom_qty-((order.price_unit*order.product_uom_qty)*categ.trade_discounts)/100)*categ.quantity_discount)/100,
                                'special_discount':categ.special_discount,
                                'special_amount':((order.price_unit*order.product_uom_qty-((((order.price_unit*order.product_uom_qty)*categ.trade_discounts)/100)+((order.price_unit*order.product_uom_qty-((order.price_unit*order.product_uom_qty)*categ.trade_discounts)/100)*categ.quantity_discount)/100))*categ.special_discount)/100})
                    else:
                        if order.category_ids.id == categ.category.id:
                            order.order_id.cal_done = True
                            order.update({
                                'trade_discount':categ.trade_discounts,
                                'trade_amount':((order.price_unit*order.mtrs)*categ.trade_discounts)/100,
                                'quantity_discount':categ.quantity_discount,
                                'quantity_amount':((order.price_unit*order.mtrs-((order.price_unit*order.mtrs)*categ.trade_discounts)/100)*categ.quantity_discount)/100,
                                'special_discount':categ.special_discount,
                                'special_amount':((order.price_unit*order.mtrs-((((order.price_unit*order.mtrs)*categ.trade_discounts)/100)+((order.price_unit*order.mtrs-((order.price_unit*order.mtrs)*categ.trade_discounts)/100)*categ.quantity_discount)/100))*categ.special_discount)/100})
                else:
                    order.order_id.cal_done=False
                categ.sale_discount_id.cal_done=True

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(force_company=self.company_id.id, default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'confirmation_date': self.confirmation_date,
            'z_delivered_to' : self.z_delivered_to,
            'payment_method': self.payment_method.name,
            'order_type': self.order_type.name,
            'ext_doc_no': self.ext_doc_no,
            'custom_po_no': self.custom_po_no,
            'po_date': self.po_date,
            'vehicle': self.vehicle.id,
            'port_of_discharge':self.port_of_discharge.id,
            'port_of_destination':self.port_of_destination.id,
            'country_of_origin_goods':self.country_of_origin_goods.id,
            'country_of_final_destination':self.country_of_final_destination.id,
            'pre_carriage':self.pre_carriage,
            'carriage':self.carriage,
            'export_shipment_method':self.export_shipment_method.id,
            'type_of_container':self.type_of_container.id,
            'proforma_sequence':self.proforma_sequence,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
        }
        return invoice_vals




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    category_ids = fields.Many2one('item.category',string="Item Category",related="product_id.item_category")
    product_uom_qty = fields.Float(string='Quantity', digits=(16,0),required=True, default=1.0)

    trade_discount = fields.Float(string='Trade Disc(%)', digits=dp.get_precision('Trade Discount'), default=0.0)
    trade_amount = fields.Float('Trade Disc(₹)', digits=dp.get_precision('Price'), default=0.0,store=True,track_visibility='always')
    trade_discount_id = fields.Many2many('sale.discount','trade_id',store=True,string="Trade Discount" ,domain="[('discount_type','=','trade')]",default=lambda self: self.env['sale.discount'].search([('id', '=', 3)]).ids)
    quantity_discount = fields.Float(string='Quantity Disc(%)', digits=dp.get_precision('Quantity Discount'), default=0.0)
    quantity_amount = fields.Float('Quantity Disc(₹)', digits=dp.get_precision('Price'), default=0.0,store=True,track_visibility='always')
    quantity_discount_id = fields.Many2many('sale.discount','quantity_id',store=True,string="Quantity Discount",domain="[('discount_type','=','quantity')]",default=lambda self: self.env['sale.discount'].search([('id', '=', 1)]).ids)
    special_discount = fields.Float(string='Special Disc(%)', digits=dp.get_precision('Special Discount'), default=0.0)
    special_amount = fields.Float('Special Disc(₹)', digits=dp.get_precision('Price'), default=0.0,store=True,track_visibility='always')
    special_discount_id = fields.Many2many('sale.discount','special_id',store=True,string="Special Discount",domain="[('discount_type','=','special')]",default=lambda self: self.env['sale.discount'].search([('id', '=', 2)]).ids)

    dis_price_unit = fields.Float('Price/UOM Qty', required=True,digits=(16,3), default=0.0)
    total_prod_weight = fields.Float('Total Weight(kg)',compute="calculate_weight",store=True)
    price_unit = fields.Float('Discounted Price', required=True,digits='Product Price', default=0.0)
    gross_subtotal = fields.Monetary('Gross ', required=True, digits=dp.get_precision('Product Price'), default=0.0,store=True,compute="_calculate_dis_price")

    #alternative meters
    mtrs = fields.Float(string="Alt.UOM QTY",digits=dp.get_precision('Meters'),default=0.00,store=True,compute="cal_alternative")
    alt_uom = fields.Many2one('uom.uom',string='Alt.Uom',readonly=True,related="product_id.product_tmpl_id.alternate_uom",store=True)
    gross_total = fields.Monetary(compute='_compute_gross_total_amount',digits=dp.get_precision('Product Price'), string='Gross Subtotal', readonly=True, store=True)
    weight = fields.Float(string="Weight",digits=dp.get_precision('Weight'),default=0.00,store=True)
    base_price = fields.Float(string="Base Price",digits=dp.get_precision('Base Price'),default=0.00,store=True)
    order_type = fields.Many2one('sale.order.type',string='Order Type',related="order_id.order_type",store=True)
    z_fix_price = fields.Float(string='Fixed Price',store=True)
    z_lst_price = fields.Float(string='Sale Price',store=True)

    @api.onchange('product_id')
    def change_weight_base_price(self):
        for line in self:
            if line.order_type.name != 'PROJECT ORDER':
                line.weight = 0
                line.base_price = 0
                line.z_lst_price = line.product_id.lst_price
                line.dis_price_unit = line.z_lst_price
                line.price_unit = line.dis_price_unit

    
    @api.onchange('product_id','quantity')
    def change_fixed_price(self):
        for line in self:
            for aj in line.order_id:
                var = self.env['product.pricelist.item'].search([('pricelist_id','=',aj.pricelist_id.id),('product_tmpl_id','=',line.product_id.product_tmpl_id.id)])
                for l in var:
                    line.z_fix_price = l.fixed_price

    
    @api.onchange('product_id','quantity')
    def onchange_fix_price(self):
        for line in self:
            #if line.z_fix_price == 0:
                #print('+++++++++++++++++++++++++++++++++++++++++++++++++++')
                # line.dis_price_unit = line.z_lst_price
                # line.price_unit = line.dis_price_unit
            if line.z_fix_price > 0:
                line.dis_price_unit = line.z_fix_price
                line.price_unit = line.dis_price_unit
            else:
                #print('QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ')
                line.dis_price_unit = line.z_lst_price
                line.price_unit = line.dis_price_unit




    @api.depends('product_id','product_uom_qty')
    def cal_alternative(self):
        for line in self:
            if line.product_id.product_tmpl_id.conversion:
                line.mtrs = line.product_uom_qty * line.product_id.product_tmpl_id.conversion
            else:
                line.mtrs = 0.0

    @api.depends('product_id','product_uom_qty','dis_price_unit')
    def _compute_gross_total_amount(self):
        for line in self:
            if not line.mtrs:
                line.gross_total = line.dis_price_unit * line.product_uom_qty
            else:
                line.gross_total = line.dis_price_unit * line.mtrs


    
    @api.onchange('product_id','product_uom_qty','order_id.order_type','weight','base_price')
    def change_discount_price_unit(self):
        for line in self:
            if line.order_id.order_type.name == 'PROJECT ORDER':
                line.dis_price_unit = line.weight * line.base_price
                line.price_unit = line.dis_price_unit
            # else:
            #     #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            #     line.z_lst_price = line.product_id.lst_price
            #     line.price_unit = line.dis_price_unit



    @api.onchange('dis_price_unit')
    def change_dis_price_unit(self):
        for line in self:
            line.price_unit = line.dis_price_unit

    @api.depends('product_uom_qty','product_id')
    def calculate_weight(self):
        for line in self:
            line.total_prod_weight = line.product_uom_qty * line.product_id.weight

    @api.depends('trade_amount','quantity_amount','special_amount')
    def _calculate_dis_price(self):
        for line in self:
            if not line.mtrs:
                line.gross_subtotal = ((line.dis_price_unit * line.product_uom_qty) - (line.trade_amount + line.quantity_amount + line.special_amount))
                line.price_unit = line.gross_subtotal / line.product_uom_qty
            else:
                line.gross_subtotal = ((line.dis_price_unit * line.mtrs) - (line.trade_amount + line.quantity_amount + line.special_amount))
                line.price_unit = line.gross_subtotal / line.mtrs



    
    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        # self.ensure_one()
        # res = {}
       # account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        # if not account:
        #     raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
        #         (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        # fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        # if fpos:
        #     account = fpos.map_account(account)
        self.ensure_one()
        qty_back = 0
        total = 0 
        trade = quant = special = price = tot = 0
        if self.mtrs:
            if self.qty_delivered != 0:
                qty_back = self.qty_delivered * self.product_id.conversion
                price = self.dis_price_unit * qty_back
                tot = price/self.qty_to_invoice
                if self.trade_discount or self.quantity_discount or self.special_discount:
                    trade = (tot * self.trade_discount) / 100
                    quant = (tot * self.quantity_discount) / 100
                    special = (tot * self.special_discount) / 100
                    total = (tot) - (trade + quant + special)
            else:
                qty_back = self.mtrs
                price = self.dis_price_unit * qty_back
                tot = price/self.qty_to_invoice
                if self.trade_discount or self.quantity_discount or self.special_discount:
                    trade = (tot * self.trade_discount) / 100
                    quant = (tot * self.quantity_discount) / 100
                    special = (tot * self.special_discount) / 100
                    total = (tot) - (trade + quant + special)
        else:
            total = self.dis_price_unit
        return{
            'display_type': self.display_type,
            'name': self.name,
            'sequence': self.sequence,
            #'origin': self.order_id.name,
            #'account_id': account.id,
            'price_unit': total,
            'dis_price_unit':self.dis_price_unit,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'alt_uom': self.alt_uom.id,
            'mtrs': qty_back or False,
            'total_prod_weight':self.total_prod_weight,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'category_ids':self.category_ids.id,
            'trade_discount':self.trade_discount,
            'quantity_discount':self.quantity_discount,
            'special_discount':self.special_discount,
            'l10n_in_hsn':self.l10n_in_hsn,
            'analytic_account_id': self.order_id.analytic_account_id.id,
            #'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            #'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        # return res


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'mtrs', 'tax_id')
    def _compute_amount(self):
        for line in self:
            if not line.mtrs:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
            if line.mtrs:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.mtrs, product=line.product_id, partner=line.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

