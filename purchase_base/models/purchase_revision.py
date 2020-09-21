from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    current_revision_id = fields.Many2one('purchase.order','Current revision',readonly=True,copy=True)
    old_revision_ids = fields.One2many('purchase.order','current_revision_id','Old revisions',readonly=True,context={'active_test': False})
    revision_number = fields.Integer('Revision',copy=False)
    unrevisioned_name = fields.Char('Unrevisioned Name',copy=True,readonly=True)
    active = fields.Boolean('Active',default=True,copy=True)  
    purchase_line = fields.One2many('purchase.order', 'old_revision_ids' )  
 

    
    @api.model
    def create(self, vals):
        if 'unrevisioned_name' not in vals:
            if vals.get('name', 'New') == 'New':
                seq = self.env['ir.sequence']
                vals['name']  =seq.next_by_code('purchase.order') or '/'
            vals['unrevisioned_name'] = vals['name']
        return super(PurchaseOrder, self).create(vals)
    
    
    def action_revision(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('purchase', 'purchase_order_form')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(purchase_revision_history=True).copy()
        self.write({'state': 'draft'})
        self.old_revision_ids.write({'state': 'cancel'})
        purchase_line = self.mapped('order_line')
        self.purchase_line.write(
                {'purchase_line_id': True})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Order'),
            'res_model': 'purchase.order',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
        
    @api.returns('self', lambda value: value.id)

    def copy(self, default=None):

        if not default:
            default = {}
        if self.env.context.get('purchase_revision_history'):
            default = {}
            prev_name = self.name
            revno = self.revision_number
            if revno == 0: 
                self.unrevisioned_name = prev_name
                self.write({'revision_number': revno + 1,'name': '%s-%02d' % (self.unrevisioned_name,revno + 1)})
            
            self.write({'revision_number': revno + 1,'name': '%s-%02d' % (self.unrevisioned_name,revno + 1)})
    
            default.update({
                'name': prev_name,
                'revision_number': revno,
                'active': True,
                'current_revision_id': self.id,
                'unrevisioned_name': self.unrevisioned_name
                })
        return super(PurchaseOrder, self).copy(default=default)

    
   

    
   
