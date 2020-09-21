# -*- coding: utf-8 -*-

from odoo import api, fields, models,exceptions,_
from odoo.addons import decimal_precision as dp
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import time
import math
import datetime
from datetime import datetime

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
import pdb


_STATES = [
  ('draft', 'Draft'),
  ('to_approve', 'To be approved'),
  ('level_a_approved', 'Approved'),
  ('rejected', 'Rejected')
]


class PurchaseRequest(models.Model):

  _name = 'purchase.request'
  _description = 'Purchase Request'
  _inherit = ['mail.thread']

  @api.model
  def _company_get(self):
      company_id = self.env['res.company']._company_default_get(self._name)
      return self.env['res.company'].browse(company_id.id)

  @api.model
  def _get_default_requested_by(self):
      return self.env['res.users'].browse(self.env.uid)

  @api.model
  def _get_default_name(self):
      return self.env['ir.sequence'].get('purchase.request')

  # @api.model
  # def _default_picking_type(self):
  #     type_obj = self.env['stock.picking.type']
  #     company_id = self.env.context.get('company_id') or \
  #         self.env.user.company_id.id
  #     types = type_obj.search([('code', '=', 'incoming'),
  #                              ('warehouse_id.company_id', '=', company_id)])
  #     if not types:
  #         types = type_obj.search([('code', '=', 'incoming'),
  #                                  ('warehouse_id', '=', False)])
  #     return types[:1]

  
  @api.depends('state')
  def _compute_is_editable(self):
      for rec in self:
          if rec.state in ('level_b_approved', 'rejected'):
              rec.is_editable = False
          else:
              rec.is_editable = True

  
  def _track_subtype(self, init_values):
      for rec in self:
          if 'state' in init_values and rec.state == 'to_approve':
              return 'skit_po_request.purchase_request_approve'
          elif 'state' in init_values and rec.state == 'level_a_approved':
              return 'skit_po_request.purchase_request_approved'
          elif 'state' in init_values and rec.state == 'level_b_approved':
              return 'skit_po_request.purchase_request_approved'
          elif 'state' in init_values and rec.state == 'rejected':
              return 'skit_po_request.purchase_request_rejected'
      return super(PurchaseRequest, self)._track_subtype(init_values)

  
  def copy(self, default=None):
      default = dict(default or {})
      self.ensure_one()
      default.update({
          'state': 'draft',
          # 'name': self.env['ir.sequence'].get('purchase.request'),
      })
      return super(PurchaseRequest, self).copy(default)

  @api.model
  def create(self, vals):
      new_sqe= self.env['ir.sequence'].get('purchase.request')
      vals.update({'name': new_sqe})
      if vals.get('assigned_to'):
          request.message_subscribe(request.assigned_to.ids)
      request = super(PurchaseRequest, self).create(vals)
      return request

  
  # def write(self, vals):
  #     res = super(PurchaseRequest, self).write(vals)
  #     for request in self:
  #         if vals.get('assigned_to'):
  #             self.message_subscribe(request.assigned_to.ids)
  #     return res

  
  def button_draft(self):
      for rec in self:
          rec.state = 'draft'
      return True

  
  def button_to_approve(self):
      for rec in self:
        rec.state = 'to_approve'
      return True

  
  def button_approved(self):
      for rec in self:
        if rec.z_login_id:
          if rec.state == 'to_approve':
            var = self.env['res.approval'].search([('id','=',rec.purchase_type.id)])
            s = False
            for lvl in var:
              for lvl_chk in lvl.z_order_line_id:
                #pdb.set_trace()
                if rec.z_login_id.id == lvl_chk.z_purchase_request_approve.id and rec.z_analytic_account.id == lvl_chk.z_analytic_account.id:
                  rec.state = 'level_a_approved'
                  rec.z_level1_approved_by = rec.purchase_type.z_order_line_id.approval_line_id.id
                  rec.z_level1_date_by = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  s = True
                  break
              if s == True:
                break
            if not s:
              raise Warning('You are not Authorized to Approve.')
          # pdb.set_trace()    
          # if rec.state == 'to_approve':
          #   va = self.env['res.approval'].search([('id','=',rec.purchase_type.id)])
          #   for lvl in va:
          #     for lvl_chk in lvl.z_order_line_id:
              # elif (lvl_chk.levels != 'level_1') and rec.purchase_type.id != lvl_chk.z_purchase_request_type.id and rec.z_analytic_account.id == lvl_chk.z_analytic_account.id:
              #   raise exceptions.Warning('You are not Authorized to Approve.')
              # elif (lvl_chk.levels != 'level_1') and rec.purchase_type.id == lvl_chk.z_purchase_request_type.id and rec.z_analytic_account.id != lvl_chk.z_analytic_account.id:
              #   raise exceptions.Warning('You are not Authorized to Approve.') 
              # else:
              #   raise exceptions.Warning('You are not Authorized to Approve.')
      return True

  # def button_approved_level2(self):
  #     for rec in self:
  #         if rec.z_login_id:
  #           # pdb.set_trace()
  #           if rec.state == 'level_a_approved':
  #             for lvl_chk in rec.z_login_id.z_order_line_id:
  #               if (lvl_chk.levels == 'level_2') and rec.purchase_type.id == lvl_chk.z_purchase_request_type.id and rec.z_analytic_account.id == lvl_chk.z_analytic_account.id:
  #                 rec.state = 'level_b_approved'
  #                 rec.z_level2_approved_by = rec.z_login_id.z_order_line_id.approval_line_id.id
  #                 rec.z_level2_date_by = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
  #           if rec.state == 'level_a_approved':
  #             for lvl_chk in rec.z_login_id.z_order_line_id :
  #               if (lvl_chk.levels != 'level_1') and rec.purchase_type.id == lvl_chk.z_purchase_request_type.id and rec.z_analytic_account.id == lvl_chk.z_analytic_account.id:
  #                 raise exceptions.Warning('You are not Authorized to Approve.')
  #               elif (lvl_chk.levels != 'level_1') and rec.purchase_type.id != lvl_chk.z_purchase_request_type.id and rec.z_analytic_account.id == lvl_chk.z_analytic_account.id:
  #                 raise exceptions.Warning('You are not Authorized to Approve.')
  #               elif (lvl_chk.levels != 'level_1') and rec.purchase_type.id == lvl_chk.z_purchase_request_type.id and rec.z_analytic_account.id != lvl_chk.z_analytic_account.id:
  #                 raise exceptions.Warning('You are not Authorized to Approve.')
  #               else:
  #                 raise exceptions.Warning('You are not Authorized to Approve.')
          
  
  def button_rejected(self):
      for rec in self:
        rec.state = 'rejected'
          
      return True

  
  def button_confirm(self):
      for order in self:
          if order.state not in ['draft', 'sent']:
              continue
          order._add_supplier_to_product()
          # Deal with double validation process
          if order.company_id.po_double_validation == 'one_step'\
                  or (order.company_id.po_double_validation == 'two_step'\
                      and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                  or order.user_has_groups('purchase.group_purchase_manager'):
              order.button_approve()
          else:
              order.write({'state': 'to approve'})

          # if order.state in ['draft','purchase']:
          #   order.write({'z_check_status': 'close'})
      return True

  name = fields.Char('Request Reference', size=32,
                     track_visibility='onchange',tracking=True)
  origin = fields.Char('Source Document', size=32,tracking=True)
  date_start = fields.Datetime('Creation date',
                               help="Date when the user initiated the "
                               "request.",
                               default=fields.Datetime.now(),
                               tracking=True)
  requested_by = fields.Many2one('res.users',
                                 'Requested by',
                                 required=True,
                                 tracking=True,
                                 default=_get_default_requested_by)
  assigned_to = fields.Many2one('res.users', 'Approver',
                                store=True,tracking=True,compute="_purchase_type")
  description = fields.Text('Description',tracking=True)
  company_id = fields.Many2one('res.company', 'Company',
                               required=True,
                               default=_company_get,
                               tracking=True)
  line_ids = fields.One2many('purchase.request.line', 'request_id',
                             'Products to Purchase',
                             readonly=False,
                             copy=True,
                             tracking=True)
  state = fields.Selection(selection=_STATES,
                           string='Approval Status',
                           index=True,
                           required=True,
                           copy=False,
                           default='draft')
  is_editable = fields.Boolean(string="Is editable",
                               compute="_compute_is_editable",
                               default=True)
  # po_status = fields.Char(string="Status",store=True,readonly=True,track_visibility='onchange')

  # picking_type_id = fields.Many2one('stock.picking.type',
  #                                   'Picking Type', required=True,
  #                                   default=_default_picking_type)
  purchase_type = fields.Many2one('res.approval',string = 'Purchase Request Type',store = True,required=True,tracking=True)
  z_check_status=fields.Selection([('open','Open'),('close','Close',)],default='open',string='Status',readonly=True)
  z_check_order = fields.Char(store = True,compute = '_check_line',string = 'Statuses')
  # z_check_order_1 = fields.Char(store = True,string = 'Status',compute = "_check_close")
  z_analytic_account = fields.Many2one('account.analytic.account',string = 'Account Analytic',store = True,required=True)
  z_level1_approved_by = fields.Many2one('res.users',string="Approved By")
  z_level1_date_by = fields.Date(string='Approved Date')
  # z_level2_approved_by = fields.Many2one('res.users',string="CEO Approved By")
  # z_level2_date_by = fields.Date(string='CEO Approved Date')
  z_manufacturing_id = fields.Many2one('mrp.production',string="Manufacturing Order References")
  z_manufacturing_order_ref = fields.Char(string='Manufacturing Order Reference',store = True,readonly=True)
  z_sale_ref = fields.Char(string='Sale Order Reference',store = True,readonly=True)
  z_login_id = fields.Many2one('res.users',string="Current User",compute="_get_login_id")
  #z_partner_id = fields.Many2one('res.partner',string="Vendor")

  
  @api.depends('company_id')
  def _get_login_id(self):
    user_obj = self.env['res.users'].search([])
    for user_login in user_obj:
      current_login= self.env.user
      if user_login == current_login:
        self.z_login_id = current_login
  
  @api.depends('line_ids.check_boolean')
  def _check_line(self):
    self.z_check_order = 'open'
    for line in self:
      for l in line.line_ids:
        if l.check_boolean == True:
          line.z_check_order = "close"
        if l.check_boolean == False:
          line.z_check_order = "open"

  
  # @api.depends('line_ids.check_boolean','z_check_order')
  # def _check_close(self):
  #   # pdb.set_trace()
  #   for line in self:
  #     if not line.z_check_order:
  #       line.z_check_order_1 = "Close"
  #     if line.z_check_order == "Close":
  #       line.z_check_order_1 = "Close"
        

  
  # @api.depends('purchase_type')
  # def _purchase_type(self):
  #   for line in self:
      # purchase = self.env['res.approval.line'].search([('z_purchase_request_type','=',line.purchase_type.id)])
      # for l in purchase:
        # line.assigned_to = l.approval_line_id.id

  
  def button_check(self):
    for line in self:
      for rec in line.line_ids:
        purchases = self.env['stock.quant'].search([('product_id','=',rec.product_id.id)])
        qty_onhand = qty_reserve = projected_quantity = 0.0
        for l in purchases:
          if l.location_id.usage == 'internal':
            qty_onhand += l.quantity
            qty_reserve += l.reserved_quantity
            projected_quantity += rec.z_qty_onhand - rec.z_qty_reserve
        rec.z_qty_onhand = qty_onhand
        rec.z_qty_reserve = qty_reserve
        rec.z_projected_quantity = projected_quantity


  


class PurchaseRequestLine(models.Model):

  _name = "purchase.request.line"
  _description = "Purchase Request Line"
  # _inherit = ['mail.thread']

  # @api.onchange('z_balance_quantity','z_balance_quantity_order')
  # def _onchange_purchase_order_origin(self):
  #     for l in self:
        

  
  @api.depends('product_id', 'name', 'product_uom_id', 'product_qty',
               'analytic_account_id', 'date_required', 'specifications')
  def _compute_is_editable(self):
      for rec in self:
          if rec.request_id.state in ('level_b_approved', 'rejected'):
              rec.is_editable = False
          else:
              rec.is_editable = True

  @api.depends('product_id')
  def _compute_supplier_id(self):
      for rec in self:
          if rec.product_id:
              if rec.product_id.seller_ids:
                  rec.supplier_id = rec.product_id.seller_ids[0].name
              else:
                  rec.supplier_id = False
          else:
              rec.supplier_id = False

  @api.onchange('product_id', 'product_uom_id')
  def onchange_product_id(self):
      if self.product_id:
          name = self.product_id.name
          if self.product_id.code:
              name = '[%s] %s' % (name, self.product_id.code)
          if self.product_id.description_purchase:
              name += '\n' + self.product_id.description_purchase
          self.product_uom_id = self.product_id.uom_id.id
          self.product_qty = 1
          self.name = name

  product_id = fields.Many2one(
      'product.product', 'Product',
      domain=[('purchase_ok', '=', True)],
      tracking=True)
  name = fields.Char('Description', size=256,
                     ttracking=True)
  product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure',
                                   tracking=True)
  product_qty = fields.Float('Quantity',tracking=True)
  request_id = fields.Many2one('purchase.request',
                               'Purchase Request',
                               ondelete='cascade', readonly=True,tracking=True)
  company_id = fields.Many2one('res.company',
                               related='request_id.company_id',
                               string='Company',
                               store=True, readonly=True)
  analytic_account_id = fields.Many2one('account.analytic.account',
                                        'Analytic Account',related = 'request_id.z_analytic_account',
                                        tracking=True)
  requested_by = fields.Many2one('res.users',
                                 related='request_id.requested_by',
                                 string='Requested by',
                                 store=True, readonly=True,tracking=True)
  assigned_to = fields.Many2one('res.users',
                                related='request_id.assigned_to',
                                string='Assigned to',
                                store=True, readonly=True,tracking=True)
  date_start = fields.Datetime(related='request_id.date_start',
                               string='Request Date', readonly=True,
                               store=True,tracking=True)
  description = fields.Text(related='request_id.description',
                            string='Descriptions', readonly=True,
                            store=True,tracking=True)
  origin = fields.Char(related='request_id.origin',
                       size=32, string='Source Document', readonly=True,
                       store=True)
  date_required = fields.Datetime(string='Required Date', required=True,
                                  track_visibility='onchange',
                                  default=fields.Datetime.now())
  is_editable = fields.Boolean(string='Is editable',
                               compute="_compute_is_editable",
                               readonly=True,tracking=True)
  specifications = fields.Text(string='Specifications')
  request_state = fields.Selection(string='Request state',
                                   readonly=True,
                                   related='request_id.state',
                                   selection=_STATES,
                                   store=True,tracking=True)
  supplier_id = fields.Many2one('res.partner',
                                string='Preferred supplier',
                                compute="_compute_supplier_id",tracking=True)

  # procurement_id = fields.Many2one('procurement.order',
  #                                  'Procurement Order',
  #                                  readonly=True)
  purchase_id = fields.Char(
                                "Purchase Order",store = True,
                                invisible = True)
  z_balance_quantity = fields.Float('Balance Quantity',store = True)
  z_balance_quantity_order = fields.Float('Purchase order Quantity',store = True)
  z_qty_onhand = fields.Float(string="Qty On Hand",tracking=True)
  z_qty_reserve = fields.Float(string="Qty Reserved")
  z_projected_quantity = fields.Float(string="Projected Quantity")
  # z_check = fields.Char(string="Status",store=True,track_visibility="always",related="request_id.z_check_order_1")
  check_boolean = fields.Boolean('Done',store = True)
  check_status = fields.Char('Check Status',store = True)
  categ_types = fields.Selection([('products','Products'),('services','Services'),('assets','Assets'),('charge','Charges')],'Category',default='products')

  def write(self, values):
    # pdb.set_trace()
    if 'product_id' in values:
      for line in self:
        if line.request_id:
          line.request_id.message_post_with_view('skit_po_request.track_po_line_template1',values={'line': line, 'product_id': values['product_id']},subtype_id=self.env.ref('mail.mt_note').id)
    if 'product_qty' in values:
      for line in self:
        if line.request_id:
          line.request_id.message_post_with_view('skit_po_request.track_po_line_template1',values={'line': line, 'product_qty': values['product_qty']},subtype_id=self.env.ref('mail.mt_note').id)
    if 'date_required' in values:
      for line in self:
        if line.request_id:
          line.request_id.message_post_with_view('skit_po_request.track_po_line_template1',values={'line': line, 'date_required': values['date_required']},subtype_id=self.env.ref('mail.mt_note').id)
    return super().write(values)
 
  
  def unlink(self):
    for line in self:
      if line.request_id.z_check_status == "Close":
        raise UserError(_('Cannot delete a purchase Request order line which is in state Close'))


  # @api.onchange('categ_types')
  # def onchange_use_insurance(self):
  #   res = {}
  #   if self.categ_types == 'charge':
  #     res['domain'] = {'product_id': [('purchase_ok', '=', True),'&',('type', '=', 'service'),('categ_charge', '=', True)]}
  #   elif self.categ_types == 'services':
  #     res['domain'] = {'product_id': [('purchase_ok', '=', True),'&',('type', '=', 'service'),('categ_service', '=', True)]}
  #   elif self.categ_types == 'assets':
  #     res['domain'] = {'product_id': [('purchase_ok', '=', True),'&',('type', '=', ['product','consu']),('categ_assets', '=', True)]}
  #   else:
  #     res['domain'] = {'product_id': [('purchase_ok', '=', True),'&',('type', '=', ['product','consu']),('categ_product', '=', True)]}
  #   return res
  @api.onchange('check_boolean')
  def _change_check_status(self):
    for lit in self:
      count = self.env['purchase.request.line'].search_count([('check_boolean','=',lit.check_boolean)])
      lit.check_status = str(count)
'''  @api.multi
  def generate_po_order(self):
    for line in self:
      mo_count = self.env['purchase.order.line']
      if not mo_count:
        vals = {
        'name': line.request_id.name,
        'product_id': line.product_id.id,
        'product_qty':line.product_qty,
        'date_planned':line.date_required,
        'product_uom':line.product_uom_id,'purchase_request_line':line.id,
                'categ_types':line.categ_types,
                }
          return vals'''
class PurchaseRequestLine(models.Model):
  _name = "purchase.type"
  _description='Purchase Type'
  name = fields.Char('Name',store = True)
class PurchaseOrder(models.Model):
  _inherit = 'purchase.order'
  purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request' , domain ="[('z_check_status','=','open'),('state','=','level_a_approved')]")
  reference = fields.Char('Reference',store = True)
  z_balance_check = fields.Boolean(string="Balance Check",store=True)

  
  @api.onchange('reference')
  def onchange_analytic_id(self):
    for line in self:
      pur = self.env['purchase.request'].search([('name','=',line.reference)])
      for l in pur:
        line.z_account_analytic_id = l.z_analytic_account.id

  
  
  @api.onchange('reference')
  def _onchange_sale(self):
    for line in self:
      for l in line.order_line:
        line.origin = l.purchase_request_id.z_sale_ref 

  
  @api.onchange('reference')
  def _onchange_boolean(self):
    for line in self:
      line.z_balance_check = True
      for l in line.order_line:
        if line.z_balance_check == True:
          if l.z_balance_qty > 0:
            l.product_qty = l.z_balance_qty

  
  @api.onchange('purchase_request_id')
  def _onchange_allowed_purchase_ids(self):
      result = {}

      purchase_line_ids = self.order_line.mapped('purchase_request_line')
      purchase_ids = self.order_line.mapped('purchase_request_id').filtered(lambda r: r.line_ids <= purchase_line_ids)

      return result

  # Load all unsold PO lines
  @api.onchange('purchase_request_id')
  def purchase_order_change(self):
      if not self.purchase_request_id:
          self.purchase_request_id = self.purchase_request_id
          return {}
      new_lines = self.env['purchase.order.line']
      for line in self.purchase_request_id.line_ids - self.order_line.mapped('purchase_request_line'):
        if not line.check_boolean:
          data = self._prepare_invoice_line_from_po_lines(line)
          new_line = new_lines.new(data)
          new_line._set_additional_po_order_fields(self)
          new_lines += new_line
      self.order_line += new_lines
      self.env.context = dict(self.env.context, from_purchase_order_change=True)
      self.purchase_request_id = False
      #changing the final_display boolean value to true once the po is used.
      return {}

      
  def _prepare_invoice_line_from_po_lines(self, line):
    invoice_line = self.env['purchase.order.line']
    price = 0.0
    for l in line.product_id.product_tmpl_id.seller_ids:
      if l.name == self.partner_id:
        price = l.price
    
    data = {
      'purchase_request_id': line.request_id.id,
      'name': line.product_id.name,
      'product_id': line.product_id.id,
      'product_qty':line.product_qty,
      'z_balance_qty':line.z_balance_quantity,
      'product_uom': line.product_id.uom_po_id.id,
      'date_planned':line.date_required,
      'purchase_request_line':line.id,
      'price_unit':price,
      'taxes_id':line.product_id.supplier_taxes_id,
      'account_analytic_id':line.analytic_account_id.id
      }
    return data
    

  @api.onchange('order_line')
  def _onchange_purchase_order_origin(self):
      purchase_order_ids = self.order_line.mapped('purchase_request_id')
      if purchase_order_ids:
          self.reference = ', '.join(purchase_order_ids.mapped('name'))
          if not self.origin and self.reference:
              self.origin = self.reference
  
  def button_confirm(self):
      for order in self:
          if order.state not in ['draft', 'sent']:
              continue
          order._add_supplier_to_product()
          # Deal with double validation process
          if order.company_id.po_double_validation == 'one_step'\
                  or (order.company_id.po_double_validation == 'two_step'\
                      and order.amount_total < self.env.user.company_id.currency_id._convert(
                          order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                  or order.user_has_groups('purchase.group_purchase_manager'):
              order.button_approve()
          else:
              order.write({'state': 'to approve'})
          for l in order.order_line:
            if l.purchase_request_line:
              for line in l:
                  line.purchase_request_line.z_balance_quantity_order += line.product_qty
                  line.purchase_request_line.z_balance_quantity = (line.purchase_request_line.product_qty)-(line.purchase_request_line.z_balance_quantity_order)
                  purchase_order = l.mapped('order_id')
                  if purchase_order:
                    line.purchase_request_line.purchase_id = ', '.join(purchase_order.mapped('name'))
                  if line.purchase_request_line.z_balance_quantity <= 0.00:
                    line.purchase_request_line.check_boolean = True

          # pdb.set_trace()
          if order.state in ['draft', 'purchase']:
            if order.reference:
              val = self.env['purchase.request'].search([('name','=',order.reference),('z_check_order','=','close')])
              if val:
                val.write({'z_check_status':'close'})
              #line.purchase_request_line.z_balance_quantity = 
              #line.purchase_request_line.z_balance_quantity = (line.product_qty)-(line.purchase_request_line.product_qty)
      return True
class PurchaseOrderLine(models.Model):
  _inherit = 'purchase.order.line'
  purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
  purchase_request_line = fields.Many2one('purchase.request.line', string='Purchases Request')
  z_balance_qty = fields.Float(string="Balance Qty")

  
  @api.onchange('product_id')
  def _onchange_product_uom(self):
    for line in self:
      line.product_uom = line.product_id.uom_po_id


  def _set_additional_po_order_fields(self, invoice):
      """ Some modules, such as Purchase, provide a feature to add automatically pre-filled
          invoice lines. However, these modules might not be aware of extra fields which are
          added by extensions of the accounting module.
          This method is intended to be overridden by these extensions, so that any new field can
          easily be auto-filled as well.
          :param invoice : account.invoice corresponding record
          :rtype line : account.invoice.line record
      """
      pass  