

from odoo import api, fields, models,exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
import pdb


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([('draft', 'Quotation'),
                              ('sent', 'Quotation Sent'),
                              ('to approve', 'To Approve'),
                              ('approved', 'Approved'),
                              ('waiting_for_approval','Credit Blocked'),
                              ('credit','Credit Cleared'),
                              ('to_confirm','To Confirm'),
                              ('revised','Revised'),
                              ('sale', 'Sales Order'),
                              ('done', 'Locked'),
                              ('cancel', 'Cancelled'),],
                             string='Status', readonly=True, copy=False,
                             index=True, track_visibility='onchange',
                             track_sequence=3, default='draft')
    to_approve = fields.Boolean('To Approve',compute='_action_state')
    z_invisible = fields.Char('Invisible',compute="_check_line")
    Z_check_value = fields.Boolean('Customer Acknowledgment',index=True,default=False,track_visibility='onchange',compute='_compute_z_customer_approval')
    z_price = fields.Char('Price',compute='_request_price_check')
    z_state = fields.Char('Approval Status',compute='_compute_check_state')
    z_revise_visible = fields.Char('Revise',store=True,compute="_compute_revise")
    z_revise_invisible = fields.Char("Revise",store=True,compute="_compute_invisiblerevise")
    z_action_state = fields.Boolean(string="Action Approve Visibility",compute="display_approve_order")
    product_packaging = fields.Many2one('product.packaging',string="Package",domain="[('product_id', '=', product_id)]")



    
    @api.depends('order_line.z_revise')
    def _compute_revise(self):
      self.z_revise_visible = False
      for line in self:
        for l in line.order_line:
          if l.z_revise == True:
            line.z_revise_visible = "Open"

    
    @api.depends('order_line.z_revise','z_revise_visible')
    def _compute_invisiblerevise(self):
      for line in self:
        if not line.z_revise_visible:
          line.z_revise_invisible = "Close"
        else:
          line.z_revise_invisible = False

    @api.depends('order_line.z_customer_approval')
    def _compute_z_customer_approval(self):
      self.Z_check_value = False
      for line in self:
        for l in line.order_line:
          if l.z_customer_approval == True:
            line.Z_check_value = True



    
    # @api.depends('pricelist_id')
    # def _compute_pricelist(self):
    #   for l in self.order_line:
    #     product_id = l.product_id
    #     for line in self:
    #       var = self.env['product.pricelist.item'].search([('product_tmpl_id', '=', l.product_id.product_tmpl_id.id),
    #         ('pricelist_id','=',line.pricelist_id.id)])
    #       for rec in var:
    #         line.z_pricelist = rec.fixed_price

    # @api.constrains('Z_check_value')
    # def validate_confirm_order(self):
    #   if not self.Z_check_value:
    #     raise ValidationError(_("Check Customer Acknowledgment"))

    
    def action_confirm(self):
      for l in self:
        for line in l.order_line:
          if line.z_revise == True:
            if not l.Z_check_value:
            #   if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            #       raise UserError(_(
            #           'It is not allowed to confirm an order in the following states: %s'
            #       ) % (', '.join(self._get_forbidden_state_confirm())))

            #   for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            #       order.message_subscribe([order.partner_id.id])
            #   self.write({
            #       'state': 'sale',
            #       'confirmation_date': fields.Datetime.now()
            #   })
            #   self._action_confirm()
            #   if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            #       self.action_done()
            #   return True
            # else:
              raise ValidationError(_("Check Customer Acknowledgment"))

      return super(SaleOrder, self).action_confirm()


    
    @api.depends('order_line.z_customer_approval')
    def _compute_check_state(self):
      self.z_state = False
      for line in self:
        for l in line.order_line:
          if l.z_customer_approval == True:
            line.z_state = 'Customer Approved'
          else:
            line.z_state = False


    
    @api.depends('order_line.z_customer_approval')
    def _check_line(self):
      self.z_invisible = "Open"
      for line in self:
        for l in line.order_line:
          if l.z_customer_approval == False:
            line.z_invisible = "Open"
          else:
            line.z_invisible = "Close"

    
    @api.depends('order_line.z_check')
    def _request_price_check(self):
      self.z_price = 'close'
      for line in self:
        for l in line.order_line:
          if l.z_check == True:
            line.z_price = 'open'
          # elif l.z_check == False:
          #   line.z_price = 'close'

    
    def _action_state(self):
      self.to_approve = False
      for rec in self:
        if rec.state == 'to approve':
          rec.to_approve = True

    
    def _make_url(self, record_id, model_name, menu_id, action_id):
        ir_param = self.env['ir.config_parameter'].sudo()
        base_url = ir_param.get_param('web.base.url')
        if base_url:
            base_url += \
                '/web?#id=%s&action=%s&model=%s&view_type=form&menu_id=%s' \
                % (record_id, action_id, model_name, menu_id)
        return base_url

    
    def send_double_approval_email(self, authorized_group, order):
        authorized_users = \
            self.env['res.users'].search(
                [('groups_id', '=', authorized_group.id)])
        menu_id = self.env.ref('sale.menu_sale_quotations').id
        action_id = self.env.ref('sale.action_quotations_with_onboarding').id
        so_url = order._make_url(order.id, order._name, menu_id, action_id)
        if authorized_users:
            for au_user in authorized_users:
                email_body = ''' <span style='font-style: 16px;font-weight:
                 bold;'>Dear, %s</span>''' % (au_user.name) + ''' <br/><br/>
                 ''' + ''' <span style='font-style: 14px;'> A Quotation from
                  <span style='font-weight: bold;'>%s</span> is awaiting for
                  your Approval to be Confirmed</span>''' % \
                       (self.env.user.name) + ''' <br/>''' + '''<span
                       style='font-style: 14px;'>Please, access it form below
                       button</span> <div style="margin-top:40px;"> <a
                       href="''' + so_url + '''" style="background-color:
                       #1abc9c; padding: 20px; text-decoration: none; color:
                        #fff; border-radius: 5px; font-size: 16px;"
                        class="o_default_snippet_text">View Quotation</a></div>
                        <br/><br/>'''
                email_id = self.env['mail.mail'].\
                    create({'subject': 'Sale-Quotation is Waiting for Approval',
                            'email_from': self.env.user.partner_id.email,
                            'email_to': au_user.partner_id.email,
                            'message_type': 'email',
                            'body_html': email_body
                            })
                email_id.send()

    
    @api.depends('order_line.z_check')
    def display_approve_order(self):
      self.z_action_state = False
      for l in self:
        for line in l.order_line:
          if line.z_check == True:
            l.z_action_state = True
          else:
            l.z_action_state = False


    
    def action_confirms(self):
      for l in self.order_line:
        price_unit = l.price_unit
        z_requested_price = l.z_requested_price
        # if l.z_orc > 0 or l.z_check == True: 
        #   z_orc = 1
        z_check = l.z_check
      for order in self:
          if order.state in ['done', 'cancel']:
              continue
          ir_param = self.env['ir.config_parameter'].sudo()
          is_double_enabled = \
              bool(ir_param.get_param(
                  'dev_sale_order_double_approval.so_double_verify'))
          if is_double_enabled:
              double_validation_amount = \
                  float(ir_param.get_param('dev_sale_order_double_approval.'
                                           'so_double_validation_amount'))
              approval_group = 'dev_sale_order_double_approval.' \
                               'double_verification_so_right'
              double_approval_rights = \
                  order.env.user.has_group(str(approval_group))
              if order.z_price == 'open':
                if order.amount_total < double_validation_amount \
                or double_approval_rights and order.z_price == 'open' and price_unit > z_requested_price:
                  authorized_group = order.env.ref(str(approval_group))
                  order.send_double_approval_email(authorized_group, order)
                  order.write({'state': 'to approve'})
              if order.z_price == 'close':
                if order.amount_total < double_validation_amount \
                or double_approval_rights or price_unit > z_requested_price or order.z_price == 'close':
                  order.state='to_confirm'
                  #return super(SaleOrder, self).action_confirm()
              else:
                  authorized_group = order.env.ref(str(approval_group))
                  order.send_double_approval_email(authorized_group, order)
                  order.write({'state': 'to approve'})
          else:
              order.state = 'to approve'
              #return super(SaleOrder, self).action_confirm()

    '''
                def confirm_sale_order(self):
                    for order in self:
                        if order.state not in ['to approve']:
                            continue
                        return super(SaleOrder, self).action_confirm()'''

    
    def action_state(self):
      for rec in self:
        for l in rec.order_line:
          # z_customer = l.z_customer_approval
          # price_unit = l.price_unit
          # z_rev = l.z_revised_price
          # z_req_price = l.z_requested_price
          # z_revise = l.z_revise
          # # z_out = l.z_out
          # if z_customer == False:
          #   #pdb.set_trace()
          #   l.price_unit = z_req_price
          #     if l.price_unit and l.z_uom_ratio > 0:
          #       l.z_sales_price_sqft = l.price_unit / l.z_uom_ratio
          #     if l.z_sales_price_sqft and l.z_uom_ratio > 0:
          #       l.price_unit = l.z_sales_price_sqft * l.z_uom_ratio
          # if z_customer == True:
          #     l.price_unit = z_rev
          #     if l.price_unit and l.z_uom_ratio > 0:
          #       l.z_sales_price_sqft = l.price_unit / l.z_uom_ratio
          #     if l.z_sales_price_sqft and l.z_uom_ratio > 0:
          #       l.price_unit = l.z_sales_price_sqft * l.z_uom_ratio
          # if not l.z_revised_price and not l.z_requested_price:
          #   l.price_unit = price_unit   
          if l.z_revise == True and l.z_customer_approval == False:
            raise UserError(_('Please Update the Customer Approval'))
          else:
            rec.write({'state':'approved',})
            



    
    def action_revised(self):
        for rec in self:
          rec.write({'state':'revised',})

    '''
                def confirm_sale_order(self):
                  for rec in self:
                    rec.write({'state':'to approve',})
                  for order in self:
                    if order.state not in ['to approve']:
                        continue
                    return super(SaleOrder, self).action_confirm()'''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class ProductionLot(models.Model):
    _inherit = 'sale.order.line'

    z_requested_price = fields.Float(string='Requested Price')
    z_check = fields.Boolean(string="Price Change Request")
    # z_orc = fields.Float('ORC/Sq.Ft')
    z_revised_price = fields.Float(string='Revised Price')
    z_customer_approval = fields.Boolean(string='Customer Approval')
    z_revise = fields.Boolean(string='Revise Price')
    # price_unit = fields.Float('Sale Price Sq. Mt', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    # z_current_user = fields.Many2one('res.users','Customer User',default=lambda self: self.env.user)
    # z_check_user = fields.Boolean('Check User',related= 'z_current_user.z_customer_approval_readonly',store = True) 
    z_sale_price = fields.Float('Sale Price')
    product_packaging = fields.Many2one( 'product.packaging', string='Package', default=False, check_company=True)
    z_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product','Storable Product')], string='Product Type', default='consu', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    price_custom = fields.Float(string='Price')
    # z_in = fields.Float('in',store=True,compute='_compute_sale_price')
    # z_out = fields.Float('out',store=True,compute='_compute_sale_price')
    # z_requested_price_ft = fields.Float(string='Requested Price')

    @api.onchange('product_id')
    def Onchange_type(self):
      for l in self:
        l.z_type = l.product_id.type

    @api.constrains('z_requested_price','z_check','z_revised_price','z_revise')
    def validate_fields(self):
      for line in self:
        if line.z_requested_price and line.z_check == False:
          raise UserError(_('Please tick the Price Change Request'))
        if line.z_revised_price and line.z_revise == False:
          raise UserError(_('Please tick the Revised Price'))

    @api.constrains('z_requested_price','z_check')
    def validate_request(self):
      for line in self:
        if line.z_check == True and line.z_requested_price == 0:
          raise UserError(_('Please check the Requested Price'))
        if line.z_check == False and line.z_requested_price > 0:
          raise UserError(_('Please tick the Price Change Request'))

    @api.constrains('product_id','product_packaging')
    def validate_package(self):
      for line in self:
        if line.product_id.type == 'product' and line.product_id.sale_ok == True and not line.product_packaging:
          raise UserError(_('Please Fill the Package'))
        

    # @api.constrains('product_id','price_unit')
    # def validate_price(self):
    #   for line in self:
    #     if line.product_id.type == 'product' and line.price_unit != line.price_custom and not line.z_check:
    #       raise UserError(_('Price is not equal to fixed price'))




    
    # @api.depends('product_id')
    # def _compute_sale_price(self):
    #   for line in self:
    #     line.z_in = float(line.product_id.list_price)
    #     if line.product_id:
    #       if line.product_id.z_uom_so_id.uom_type == 'bigger':
    #         line.z_out = float(line.product_id.z_uom_so_id.factor_inv)
    #       else:
    #         line.z_out = float(line.product_id.z_uom_so_id.factor)

    
    # @api.depends('z_in','z_out','product_id')
    # def _compute_sale_price_div(self):
    #   for line in self:
    #     for l in line.order_id:
    #       if l.z_pricelist:
    #         line.z_sale_price = float(l.z_pricelist)/float(line.z_out)
    #       else:
    #         if line.z_in and line.z_out:
    #           line.z_sale_price = float(line.z_in)/float(line.z_out)



    @api.depends('product_uom_qty', 'discount', 'tax_id','z_check','z_customer_approval','z_revised_price','z_requested_price')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
          if line.product_packaging:
            if line.z_check == True:
              price = line.z_requested_price * (1 - (line.discount or 0.0) / 100.0)
              taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
              line.update({
                  'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                  'price_total': taxes['total_included'],
                  'price_subtotal': taxes['total_excluded'],
              })
            if line.z_revise == True:
              price = line.z_revised_price * (1 - (line.discount or 0.0) / 100.0)
              taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
              line.update({
                  'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                  'price_total': taxes['total_included'],
                  'price_subtotal': taxes['total_excluded'],
              })
            if line.z_check == False and line.z_revise == False:
              price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
              taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
              line.update({
                  'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                  'price_total': taxes['total_included'],
                  'price_subtotal': taxes['total_excluded'],
              })
          if not line.product_packaging:
            if line.z_revise == False and line.z_check == False:
              price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
              taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
              line.update({
                  'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                  'price_total': taxes['total_included'],
                  'price_subtotal': taxes['total_excluded'],
              })
          if not line.product_packaging:
            if line.z_check == True:
              price = line.z_requested_price * (1 - (line.discount or 0.0) / 100.0)
              taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
              line.update({
                  'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                  'price_total': taxes['total_included'],
                  'price_subtotal': taxes['total_excluded'],
              })
            if line.z_revise == True:
              price = line.z_revised_price * (1 - (line.discount or 0.0) / 100.0)
              taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
              line.update({
                  'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                  'price_total': taxes['total_included'],
                  'price_subtotal': taxes['total_excluded'],
              })

    # @api.onchange('z_requested_price')
    # def _onchange_requested_price(self):
    #     for line in self:
    #         if line.z_requested_price:
    #             line.z_requested_price_ft = line.z_requested_price

    # @api.onchange('z_requested_price_ft')
    # def _onchange_requested_price_ft(self):
    #     for line in self:
    #         if line.z_requested_price_ft:
    #             line.z_requested_price = line.z_requested_price_ft


class ResUser(models.Model):
  _inherit = 'res.users'

  z_customer_approval_readonly = fields.Boolean('Customer Approval',store = True)