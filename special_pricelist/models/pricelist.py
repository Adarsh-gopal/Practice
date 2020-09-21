# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang



from werkzeug.urls import url_encode
import pdb
class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = _inherit

    special_pricelist = fields.Many2one('product.pricelist',string='Special Pricelist',domain="[('customer', '=', id)]")
    check_pricelist = fields.Boolean(string='Special Pricelist Applicable')
    property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Pricelist', compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist", company_dependent=False,
        help="This pricelist will be used, instead of the default one, for sales to the current partner",domain="[('customer', '!=', id)]")




class Pricelist(models.Model):
    _inherit = "product.pricelist"

    customer = fields.Many2many('res.partner',string='Customer')

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelists', check_company=True, required=False, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one("res.currency", string="Currency",store=True, readonly=False, required=False)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit = fields.Float('Price Unit', required=True, digits='Product Price', default=0.0)

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        var = self.env['product.pricelist.item'].search([('pricelist_id','=',self.order_id.partner_id.special_pricelist.id),('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
        if var:
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                    lambda ptav:
                        ptav.price_extra and
                        ptav not in product.product_template_attribute_value_ids
                )
            ]
            if no_variant_attributes_price_extra:
                product = product.with_context(
                    no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                )

            if self.order_id.partner_id.special_pricelist.discount_policy == 'with_discount':
                return product.with_context(pricelist=self.order_id.partner_id.special_pricelist.id).price
            product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)

            final_price, rule_id = self.order_id.partner_id.special_pricelist.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.partner_id.special_pricelist.id)
            if currency != self.order_id.partner_id.special_pricelist.currency_id:
                base_price = currency._convert(
                    base_price, self.order_id.partner_id.special_pricelist.currency_id,
                    self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
            # negative discounts (= surcharge) are included in the display price
            return max(base_price, final_price)
        if not var:
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                    lambda ptav:
                        ptav.price_extra and
                        ptav not in product.product_template_attribute_value_ids
                )
            ]
            if no_variant_attributes_price_extra:
                product = product.with_context(
                    no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                )

            if self.order_id.pricelist_id.discount_policy == 'with_discount':
                return product.with_context(pricelist=self.order_id.pricelist_id.id).price
            product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)

            final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
            if currency != self.order_id.pricelist_id.currency_id:
                base_price = currency._convert(
                    base_price, self.order_id.pricelist_id.currency_id,
                    self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
            # negative discounts (= surcharge) are included in the display price
            return max(base_price, final_price)


    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        var = self.env['product.pricelist.item'].search([('pricelist_id','=',self.order_id.partner_id.special_pricelist.id),('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
        if var:
            valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the is_custom values that don't belong to this template
            for pacv in self.product_custom_attribute_value_ids:
                if pacv.custom_product_template_attribute_value_id not in valid_values:
                    self.product_custom_attribute_value_ids -= pacv

            # remove the no_variant attributes that don't belong to this template
            for ptav in self.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    self.product_no_variant_attribute_value_ids -= ptav

            vals = {}
            if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
                vals['product_uom'] = self.product_id.uom_id
                vals['product_uom_qty'] = self.product_uom_qty or 1.0

            product = self.product_id.with_context(
                lang=get_lang(self.env, self.order_id.partner_id.lang).code,
                partner=self.order_id.partner_id,
                quantity=vals.get('product_uom_qty') or self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.partner_id.special_pricelist.id,
                uom=self.product_uom.id
            )


            vals.update(name=self.get_sale_order_line_multiline_description_sale(product))

            self._compute_tax_id()

            if self.order_id.partner_id.special_pricelist and self.order_id.partner_id:
                vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
            self.update(vals)

            title = False
            message = False
            result = {}
            warning = {}
            if product.sale_line_warn != 'no-message':
                title = _("Warning for %s") % product.name
                message = product.sale_line_warn_msg
                warning['title'] = title
                warning['message'] = message
                result = {'warning': warning}
                if product.sale_line_warn == 'block':
                    self.product_id = False

            return result
        if not var:
            valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the is_custom values that don't belong to this template
            for pacv in self.product_custom_attribute_value_ids:
                if pacv.custom_product_template_attribute_value_id not in valid_values:
                    self.product_custom_attribute_value_ids -= pacv

            # remove the no_variant attributes that don't belong to this template
            for ptav in self.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    self.product_no_variant_attribute_value_ids -= ptav

            vals = {}
            if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
                vals['product_uom'] = self.product_id.uom_id
                vals['product_uom_qty'] = self.product_uom_qty or 1.0

            product = self.product_id.with_context(
                lang=get_lang(self.env, self.order_id.partner_id.lang).code,
                partner=self.order_id.partner_id,
                quantity=vals.get('product_uom_qty') or self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id
            )


            vals.update(name=self.get_sale_order_line_multiline_description_sale(product))

            self._compute_tax_id()

            if self.order_id.pricelist_id and self.order_id.partner_id:
                vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
            self.update(vals)

            title = False
            message = False
            result = {}
            warning = {}
            if product.sale_line_warn != 'no-message':
                title = _("Warning for %s") % product.name
                message = product.sale_line_warn_msg
                warning['title'] = title
                warning['message'] = message
                result = {'warning': warning}
                if product.sale_line_warn == 'block':
                    self.product_id = False

            return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        var = self.env['product.pricelist.item'].search([('pricelist_id','=',self.order_id.partner_id.special_pricelist.id),('product_tmpl_id','=',self.product_id.product_tmpl_id.id)])
        if var:
            if self.order_id.partner_id.special_pricelist and self.order_id.partner_id:
                product = self.product_id.with_context(
                    lang=self.order_id.partner_id.lang,
                    partner=self.order_id.partner_id,
                    quantity=self.product_uom_qty,
                    date=self.order_id.date_order,
                    pricelist=self.order_id.partner_id.special_pricelist.id,
                    uom=self.product_uom.id,
                    fiscal_position=self.env.context.get('fiscal_position')
                )
                self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        if not var:
            if self.order_id.pricelist_id and self.order_id.partner_id:
                product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)



    @api.onchange('product_id','z_requested_price','order_id.state','z_revised_price')
    def _Onchange_Price(self):
        # pdb.set_trace()
        self.price_unit = 0.0
        for l in self:
            for line in l.order_id:
                # pdb.set_trace()

                var = self.env['product.pricelist.item'].search([('pricelist_id','=',line.partner_id.special_pricelist.id),('product_tmpl_id','=',l.product_id.product_tmpl_id.id)])
                if var:
                    for s in var:
                        if s.fixed_price:
                            l.price_unit = s.fixed_price
                            l.price_custom = s.fixed_price
                        if not s.fixed_price:
                            l.price_unit = s.percent_price
                            l.price_custom = s.percent_price
                if not var: 
                    santhosh = self.env['product.pricelist.item'].search([('pricelist_id','=',line.partner_id.property_product_pricelist.id),('product_tmpl_id','=',l.product_id.product_tmpl_id.id)])
                    for alasandi in santhosh:
                        if alasandi.fixed_price:
                            l.price_unit = alasandi.fixed_price
                            l.price_custom = alasandi.fixed_price
                        if not alasandi.fixed_price:
                            l.price_unit = alasandi.percent_price
                            l.price_custom = s.percent_price
                if l.z_requested_price > 0.0:
                    if l.z_customer_approval == False and line.state in ['approved','sale'] :
                        l.price_unit = l.z_requested_price
                if l.z_revised_price > 0.0:
                    if l.z_customer_approval == True and line.state in ['approved','sale'] :
                        l.price_unit = l.z_revised_price


    

            