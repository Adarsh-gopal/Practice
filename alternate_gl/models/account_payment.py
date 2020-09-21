# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.payment'

    alternative_gl = fields.Many2one('alternative.gl')

    def _prepare_payment_moves(self):
        data = super(AccountMove, self)._prepare_payment_moves()

        for move in data:
            if 'line_ids' in move:
                for line in move['line_ids']:
                    if self.partner_type == 'supplier' and self.partner_id.property_account_payable_id.id == line[2]['account_id']:
                        new_account = self.alternative_gl.gl_lines.filtered(lambda x: x.account_on_partner.id == line[2]['account_id']).account_to_use_instead.id
                        line[2]['account_id'] = new_account or line[2]['account_id']
                    if self.partner_type == 'customer' and self.partner_id.property_account_receivable_id.id == line[2]['account_id']:
                        new_account = self.alternative_gl.gl_lines.filtered(lambda x: x.account_on_partner.id == line[2]['account_id']).account_to_use_instead.id
                        line[2]['account_id'] = new_account or line[2]['account_id']
        return data