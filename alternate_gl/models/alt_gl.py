# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AlternativeGL(models.Model):
    _name = 'alternative.gl'
    _description = 'Alternative GL'

    name = fields.Char()
    description = fields.Char()

    gl_lines = fields.One2many('alternative.gl.line','gl_id')


class AlternativeGLLine(models.Model):
    _name = 'alternative.gl.line'
    _description = 'Alternative GL Line'

    gl_id = fields.Many2one('alternative.gl')

    account_on_partner = fields.Many2one('account.account')
    account_to_use_instead = fields.Many2one('account.account')