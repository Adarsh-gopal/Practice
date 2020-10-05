from odoo import api, models, fields
from odoo import SUPERUSER_ID


class User(models.Model):

    _inherit = ['res.users']

    employee_ids = fields.One2many('man.power', 'user_id', string='Related employees')

    
    def write(self, vals):
        """ When renaming admin user, we want its new name propagated to its related employees """
        result = super(User, self).write(vals)
        Employee = self.env['man.power']
        if vals.get('name'):
            for user in self.filtered(lambda user: user.id == SUPERUSER_ID):
                employees = Employee.search([('user_id', '=', user.id)])
                employees.write({'name': vals['name']})
        return result

    
    def _get_related_employees(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        if 'thread_model' in ctx:
            ctx['thread_model'] = 'man.power'
        return self.env['man.power'].with_context(ctx).search([('user_id', '=', self.id)])