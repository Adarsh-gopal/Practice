from random import choice
from string import digits
import calendar
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta, date


class RosterSystem(models.Model):
    _name = "roster.system"
    _description = "roster_system"
    

    '''def _default_employee(self):
        return self.env['man.power'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('man.power', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)
    department_id = fields.Many2one('man.department', string="Department", related="employee_id.department_id",
        readonly=True)'''
    from_date = fields.Date(string="From Date", default=fields.Datetime.now, required=True)
    to_date = fields.Date(string="To Date", default=fields.Datetime.now, required=True)
    one_line = fields.One2many('roster.type','many')

    days = fields.Selection([
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday')
    ], string='Week Days', default='sunday')
    
    category_types = fields.Selection([('operator','Operator'),('helper','Helper'),('cutter','Cutter Man')])
    employee_id = fields.Many2one('man.power','Employee')
    employee_type = fields.Selection([
        ('employee', 'Employee'),
        ('non_employee', 'Non Employee')
    ], string='Employee Type', default='employee')

    name = fields.Char(string="Section")
    #name = fields.Many2one('man.power', domain="[('category_types','=',category_types)]")
    roster_id = fields.Many2one('roster.type', ondelete='cascade')


    def _date_is_day_off(self, date):
        return date.weekday() in (calendar.SATURDAY, calendar.SUNDAY)

    
    def get_day(self):
        res = []
        start_date = fields.Date.from_string(self.from_date)
        for x in range(0, 31):
            color = '#d4b5f2' if self._date_is_day_off(start_date) else ''
            res.append({'day_str': start_date.strftime('%a'), 'day': start_date.day , 'color': color})
            start_date = start_date + relativedelta(days=1)
        return res


    
    def get_leave(self):
        res = []
        start_date = fields.Date.from_string(self.from_date)
        end_date = fields.Date.from_string(self.to_date)
        delta = end_date - start_date
        if delta.days < 0: 
            return None 
        for x in range(0, 31):
            color = '#42d1f4' if self.get_details() else ''
            res.append({'days': start_date.day ,'color':color})
            start_date = start_date + relativedelta(days=1)
        return res

    
    def get_details(self):
        res = []
        for x in self.env['roster.type'].search([]):
            color = '#42d1f4'
            start_date = fields.Date.from_string(x.from_date)
            end_date = fields.Date.from_string(x.to_date)
            #end_date = start_date + relativedelta(days=30)
            while start_date <= end_date:
                last_date = start_date + relativedelta(day=1, months=+1, days=-1)
                if last_date > end_date:
                    last_date = end_date
                m_days = (last_date - start_date).days + 1
                res.append({'from_date':start_date.day,'to_date':end_date.day, 'color':color, 'days': x.days, 'name':x.name.name})
                start_date = start_date + relativedelta(days=1)
                #start_date += relativedelta(day=1, months=+1)
        return res

        

    
    def get_months(self):
        # it works for geting month name between two dates.
        res = []
        start_date = fields.Date.from_string(self.from_date)
        #end_date = fields.Date.from_string(self.to_date)
        end_date = start_date + relativedelta(days=30)
        while start_date <= end_date:
            last_date = start_date + relativedelta(day=1, months=+1, days=-1)
            if last_date > end_date:
                last_date = end_date
            month_days = (last_date - start_date).days + 1
            color = '#c1bdef'
            res.append({'month_name': start_date.strftime('%B'), 'days': month_days, 'color':color})
            start_date += relativedelta(day=1, months=+1)
        return res

    
    def get_employee(self):
        res = []
        for x in self.env['roster.type'].search([]):
            res.append({'name':x.name.name})
        return res

    @api.depends('from_date','to_date','name')
    def daily_attendance(self):
        for l in self:
            if l.from_date:
                if l.to_date:
                    holidays = self.env['man.attendance'].browse(['&',('check_in','in',[l.from_date,l.to_date]),
                        ('employee_id', '=', l.name.id)
                    ])
                    flag = 'A'
                    for line in sheet:
                        if line.name.id == employee_id.id:
                            if line.check_in:
                                flag = 'P'
                    return flag

class RosterSystem(models.Model):
    _name = "roster.type"

    operator_name = fields.Char(string="Name",related="name.logger_id")


    employee_id = fields.Many2one('man.department','Employee')
    days = fields.Selection([
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday')
    ], string='Weekoff', default='sunday')
    
    category_types = fields.Selection([('operator','Operator'),('helper','Helper'),('cutter','Cutter Man')])
    employee_type = fields.Selection([('TRUE', 'Employee'),('FALSE', 'Non Employee')], string='Employee Type')
    name = fields.Many2one('man.power', domain="[('category_types','=',category_types)]",string="ID")
    from_date = fields.Date(string="FROM DATE", default=fields.Datetime.now, required=True)
    to_date = fields.Date(string="TO DATE")
    many = fields.Many2one('roster.system')