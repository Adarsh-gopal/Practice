from odoo import models, fields, api, _, exceptions

class itemCategory(models.Model):
    _inherit = "item.category"
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of invoice categ.")

    def get_grouping_key_categ(self, invoice_tds_vals):
        self.ensure_one()
        return str(invoice_tds_vals['category'])

 
    def compute_all_prod_discount(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):

        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        categ = []
        base = 0

        prec = currency.decimal_places


        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5


        for dis in self.sorted(key=lambda r: r.sequence):

            discount_amount = dis._compute_amount_product(price_unit, quantity, product, partner)
            if not round_tax:
                discount_amount = discount_amount
            else:
                discount_amount = discount_amount
            # Keep base amount used for the current tax
            
            discount_base = 10


            categ.append({
                'id': dis.id,
                'sequence': dis.sequence,
                'category': dis.name,
                'amount': discount_amount,
            })

        return {
            'categ': sorted(categ, key=lambda k: k['sequence']),
        }


 
    def compute_all_prod_invoice_discount(self, price_unit, trade_discount,quantity_discount,special_discount,currency=None, quantity=1.0, product=None, partner=None):
        #new function is interoduced to pass trade,quantity,special discounts to calculation

        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        categ = []
        base = 0

        prec = currency.decimal_places


        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5


        for dis in self.sorted(key=lambda r: r.sequence):

            discount_amount = dis._compute_amount_product(price_unit, quantity, product, partner)
            if not round_tax:
                discount_amount = discount_amount
            else:
                discount_amount = discount_amount
            # Keep base amount used for the current tax
            
            discount_base = 10


            categ.append({
                'id': dis.id,
                'sequence': dis.sequence,
                'category': dis.name,
                'amount': discount_amount,
                #values are fetched from invoice line to discount line
                'trade_discounts':trade_discount,
                'quantity_discount':quantity_discount,
                'special_discount':special_discount
            })

        return {
            'categ': sorted(categ, key=lambda k: k['sequence']),
        }

    def _compute_amount_product(self, price_unit, quantity=1.0, product=None, partner=None):
        #self.ensure_one()
        total_categ_amount=price_unit*quantity
        return total_categ_amount        