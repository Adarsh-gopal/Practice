from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import pdb

# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'

#     z_associate_count = fields.Integer(string=".",compute="associate_account")
#     z_check_order = fields.Char(store = True,compute = '_check_line',string = 'Status')
#     z_check_order_1 = fields.Char(store = True,string = 'Status',compute = "_check_close")
#     z_sale_order_id = fields.Char(string='Sale Order Reference',store=True,track_visibility='always',compute="_check_saleorder")

    
#     @api.depends('origin')
#     def _check_saleorder(self):
#         for line in self:
#             if line.origin:
#                 var = self.env['mrp.production'].search([('origin','like','S')])
#                 for l in var: 
#                     line.z_sale_order_id = l.origin
#                 variabl = self.env['mrp.production'].search([('origin','=',line.name)])
#                 for rec in variabl:
#                     if line.z_sale_order_id:
#                         line.z_sale_order_id = rec.z_sale_order_id 

    
#     @api.depends('move_raw_ids.z_purchase_check')
#     def _check_line(self):
#         for line in self:
#             if line.move_raw_ids:
#                 for l in line.move_raw_ids:
#                     if l.z_purchase_check == True:
#                         line.z_check_order = "Open"
#             else:
#                 line.z_check_order = False

    
#     @api.depends('move_raw_ids.z_purchase_check','z_check_order')
#     def _check_close(self):
#         for line in self:
#             if not line.z_check_order:
#                 line.z_check_order_1 = "Close"

    
#     def associate_account(self):
#      for partner in self:
#         po_request = self.env['purchase.request'].search([('z_manufacturing_id','=',partner.id)])
#         partner.z_associate_count = len(po_request)


    
    # def button_po_request(self):
    #     for l in self:
    #         po_count = self.env['purchase.request']
    #         if not po_count:
    #             vals = {
    #             'z_manufacturing_order_ref': l.id,
    #             'z_manufacturing_id':l.id,
    #             'z_sale_ref': l.z_sale_order_id,
    #             # 'z_analytic_account': l.analytic_account_id.id,
    #             }
    #             po_obj = self.env['purchase.request'].create(vals)
    #             move_lines_obj = self.env['purchase.request.line']
    #             for line in l.move_raw_ids:
    #                 if line.product_uom_qty > line.reserved_availability and line.product_id.purchase_ok == True:
    #                     move_line = {}
    #                     move_line = {
    #                     'product_id': line.product_id.id,
    #                     'name':line.product_id.name,
    #                     'product_qty':line.product_uom_qty - line.reserved_availability,
    #                     'request_id':po_obj.id,
    #                     }
    #                     move_lines_obj.create(move_line)

class PurchaseType(models.Model):
    _name = 'purchase.type.user'
    _description = "Purchase Type User"

    name = fields.Char('Name',store=True)

class UserRequest(models.Model):
    _name = 'res.approval'
    _description = "Res Approval"

    name = fields.Many2one('purchase.type.user','Purchase Request Type')
    z_order_line_id = fields.One2many('res.approval.line', 'approval_line_id', string='Order Lines')
    z_order_line2_id = fields.One2many('res.approval.line2', 'approval_line2_id', string='Order Lines Two')
    validation_type = fields.Selection([
  ('first_level', 'Single Validation'),
  ('second_level', 'Double Validation')
],string='Validation Type',store=True,default='first_level')
#     level_one_approver = fields.Many2many('res.users',string='Approver 1',store=True)
#     level_two_approver = fields.Many2one('res.users',string='Approver 2',store=True)
    
    # @api.model
    # def create(self, vals):
    #     for l in self.z_order_line_id:
    #         for s in self.z_order_line2_id:
    #             if not l.z_purchase_request_approve and not s.z_purchase_request_approve2:
    #                 raise ValidationError("Please Set the User Approval.")
    #     request = super(UserRequest, self).create(vals)
    #     return request

class UserTree(models.Model):
    _name = 'res.approval.line'
    _description = "Res Approval Line"

    approval_line_id = fields.Many2one('res.approval',string="Approval")
    z_purchase_request_approve = fields.Many2one('res.users',string="Approvals")
    # levels = fields.Selection([('level_1','Level 1'),('level_2','Level 2',)],default='level_1')
    # z_analytic_account = fields.Many2one('account.analytic.account',string='Analytic account')

class UserTree2(models.Model):
    _name = 'res.approval.line2'
    _description = "Res Approval Line2"

    approval_line2_id = fields.Many2one('res.approval',string="Approval")
    z_purchase_request_approve2 = fields.Many2one('res.users',string="Approvals")

class StockMove(models.Model):
    _inherit = "stock.move"

    z_purchase_check = fields.Boolean(string="Purchase Ok",store=True,track_visibility="always",related="product_id.purchase_ok")
    z_sale_order = fields.Char(string='Sale Order Reference')
