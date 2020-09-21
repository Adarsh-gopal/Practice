# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
import re


class ProductProduct(models.Model):
    _inherit = 'product.product'

    alt_code = fields.Char()

    @api.depends_context('partner_id')
    def _compute_product_code(self):
        if self.env.user.has_group('alternate_product_code.alt_code_user'):
            for product in self:
                for supplier_info in product.seller_ids:
                    if supplier_info.name.id == product._context.get('partner_id'):
                        product.code = supplier_info.product_code or product.alt_code
                        break
                else:
                    product.code = product.alt_code
        else:
            super(ProductProduct, self)._compute_product_code()

    @api.depends_context('partner_id')
    def _compute_partner_ref(self):
        if self.env.user.has_group('alternate_product_code.alt_code_user'):
            for product in self:
                for supplier_info in product.seller_ids:
                    if supplier_info.name.id == product._context.get('partner_id'):
                        product_name = supplier_info.product_name or product.alt_code or product.name
                        product.partner_ref = '%s%s' % (product.code and '[%s] ' % product.code or '', product_name)
                        break
                else:
                    product.partner_ref = product.display_name
        else:
            super(ProductProduct, self)._compute_partner_ref()



    def name_get(self):
        if self.env.user.has_group('alternate_product_code.alt_code_user'):
            def _name_get(d):
                name = d.get('name', '')
                code = self._context.get('display_default_code', True) and d.get('alt_code', False) or False
                if code:
                    name = '[%s] %s' % (code,name)
                return (d['id'], name)

            partner_id = self._context.get('partner_id')
            if partner_id:
                partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
            else:
                partner_ids = []
            company_id = self.env.context.get('company_id')

            # all user don't have access to seller and partner
            # check access and use superuser
            self.check_access_rights("read")
            self.check_access_rule("read")

            result = []

            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id`
            self.sudo().read(['name', 'alt_code', 'product_tmpl_id'], load=False)

            product_template_ids = self.sudo().mapped('product_tmpl_id').ids

            if partner_ids:
                supplier_info = self.env['product.supplierinfo'].sudo().search([
                    ('product_tmpl_id', 'in', product_template_ids),
                    ('name', 'in', partner_ids),
                ])
                # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
                # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
                supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
                supplier_info_by_template = {}
                for r in supplier_info:
                    supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
            for product in self.sudo():
                variant = product.product_template_attribute_value_ids._get_combination_name()

                name = variant and "%s (%s)" % (product.name, variant) or product.name
                sellers = []
                if partner_ids:
                    product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                    sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                    if not sellers:
                        sellers = [x for x in product_supplier_info if not x.product_id]
                    # Filter out sellers based on the company. This is done afterwards for a better
                    # code readability. At this point, only a few sellers should remain, so it should
                    # not be a performance issue.
                    if company_id:
                        sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
                if sellers:
                    for s in sellers:
                        seller_variant = s.product_name and (
                            variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                            ) or False
                        mydict = {
                                  'id': product.id,
                                  'name': seller_variant or name,
                                  'alt_code': s.product_code or product.alt_code,
                                  }
                        temp = _name_get(mydict)
                        if temp not in result:
                            result.append(temp)
                else:
                    mydict = {
                              'id': product.id,
                              'name': name,
                              'alt_code': product.alt_code,
                              }
                    result.append(_name_get(mydict))
            return result

        else:
            return super(ProductProduct, self).name_get()


    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self.env.user.has_group('alternate_product_code.alt_code_user'):
            if not args:
                args = []
            if name:
                positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
                product_ids = []
                if operator in positive_operators:
                    product_ids = self._search([('alt_code', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
                    if not product_ids:
                        product_ids = self._search([('barcode', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
                if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                    # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                    # on a database with thousands of matching products, due to the huge merge+unique needed for the
                    # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                    # Performing a quick memory merge of ids in Python will give much better performance
                    product_ids = self._search(args + [('alt_code', operator, name)], limit=limit)
                    if not limit or len(product_ids) < limit:
                        # we may underrun the limit because of dupes in the results, that's fine
                        limit2 = (limit - len(product_ids)) if limit else False
                        product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, access_rights_uid=name_get_uid)
                        product_ids.extend(product2_ids)
                elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                    domain = expression.OR([
                        ['&', ('alt_code', operator, name), ('name', operator, name)],
                        ['&', ('alt_code', '=', False), ('name', operator, name)],
                    ])
                    domain = expression.AND([args, domain])
                    product_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
                if not product_ids and operator in positive_operators:
                    ptrn = re.compile('(\[(.*?)\])')
                    res = ptrn.search(name)
                    if res:
                        product_ids = self._search([('alt_code', '=', res.group(2))] + args, limit=limit, access_rights_uid=name_get_uid)
                # still no results, partner in context: search on supplier info as last hope to find something
                if not product_ids and self._context.get('partner_id'):
                    suppliers_ids = self.env['product.supplierinfo']._search([
                        ('name', '=', self._context.get('partner_id')),
                        '|',
                        ('product_code', operator, name),
                        ('product_name', operator, name)], access_rights_uid=name_get_uid)
                    if suppliers_ids:
                        product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit, access_rights_uid=name_get_uid)
            else:
                product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
            return models.lazy_name_get(self.browse(product_ids).with_user(name_get_uid))

        else:
            return super(ProductProduct, self)._name_search(name, args, operator, limit, name_get_uid)