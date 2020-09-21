# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    alternative_gl = fields.Many2one('alternative.gl')

    def get_partner_acc(self):
        if self.alternative_gl:
            if self.type in ('in_invoice','in_refund'):
                return self.partner_id.property_account_payable_id
            elif self.type in ('out_invoice','out_refund'):
                return self.partner_id.property_account_receivable_id
            else:
                return False
        else:
            return False

    @api.onchange('alternative_gl')
    def _adapt_alt_gl(self):
        for line in self.line_ids:
            line._adapt_alt_gl()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _adapt_alt_gl(self):
        partner_acc = self.move_id.get_partner_acc()
        if partner_acc:
            new_account = self.move_id.alternative_gl.gl_lines.filtered(lambda x: x.account_on_partner == self.account_id).account_to_use_instead.id
            self.account_id = new_account or self.account_id.id

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(AccountMoveLine, self).create(vals_list)

        for line in lines:
            line._adapt_alt_gl()

        return lines

    def write(self, vals):
        res = False
        if self.move_id.alternative_gl and 'account_id' in vals:

            recevd_acc = self.env['account.account'].browse(vals['account_id'])
            vip_accounts = self.move_id.alternative_gl.gl_lines.mapped('account_to_use_instead').ids
            if vals['account_id'] in vip_accounts:
                if self.move_id.type in ('in_invoice','in_refund'):
                    real_type = recevd_acc.user_type_id.type
                    recevd_acc.user_type_id.type = 'payable'
                    
                    res = super(AccountMoveLine, self).write(vals)
                    recevd_acc.user_type_id.type = real_type
                
                elif self.move_id.type in ('out_invoice','out_refund'):
                    real_type = recevd_acc.user_type_id.type
                    recevd_acc.user_type_id.type = 'receivable'
                    
                    res = super(AccountMoveLine, self).write(vals)
                    recevd_acc.user_type_id.type = real_type

                else:
                    res = super(AccountMoveLine, self).write(vals)
            else:
                res = super(AccountMoveLine, self).write(vals)
        else:
            res = super(AccountMoveLine, self).write(vals)


        return res