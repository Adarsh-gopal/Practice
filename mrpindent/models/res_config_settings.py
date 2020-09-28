# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_auto_indent_create = fields.Boolean("Auto Material Requisition Creation",group='base.group_user',implied_group='mrpindent.group_auto_indent_create')
    

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            use_manufacturing_lead=self.env['ir.config_parameter'].sudo().get_param('mrpindent.group_auto_indent_create')
        )
        return res

    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('mrpindent.group_auto_indent_create', self.group_auto_indent_create)
