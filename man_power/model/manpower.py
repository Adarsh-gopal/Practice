import base64
import logging

from odoo import api, fields, models,exceptions,_
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError, ValidationError,Warning
from datetime import datetime
from odoo.tools import image_process
from odoo.tools.image import image_data_uri
from odoo.modules import get_module_resource
import base64


_logger = logging.getLogger(__name__)


class ManPowerMaster(models.Model):
    _name = "man.power"
    _description = "Manpower"
    _inherit = ['resource.mixin']

    @api.model
    def _default_image(self):
        image_path = get_module_resource('man_power', 'static/src/img', 'default_image.png')
        return (base64.b64encode(open(image_path, 'rb').read()))

    name = fields.Char('ID', store=True,required=True)
    user_id = fields.Many2one('res.users', 'Operator Name', related='resource_id.user_id')
    logger_id = fields.Char('Name', copy=False, index=True)
    address_home_id = fields.Char(String='Address')
    password_id = fields.Char(String='Password',required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], default="male")
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', default='single')
    work_phone = fields.Char('Work Phone')
    mobile_phone = fields.Char('Work Mobile')
    work_location = fields.Char('Work Location')
    notes = fields.Text('Notes')
    color = fields.Integer('Color Index', default=0)
    image = fields.Binary(
        "Photo", default=_default_image, attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.",store=True)
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.",store=True)
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.",store=True)
    department_id = fields.Many2one('man.department', 'Department')

    category_types = fields.Selection([('operator','Operator'),('helper','Helper'),('cutter','Cutter Man')])
    z_is_employee = fields.Boolean(string="Is an Employee",default=False)


    # defaults = {
    # 'active': 1,
    # 'image': _default_image,
    # 'color': 0,
    # }

    # @api.model 
    # def create(self, vals):
    #     tools.image_resize_images(vals) 
    #     return super(ManPowerMaster, self).create(vals)

    
    # def write(self, vals):
    #     tools.image_resize_images(vals) 
    #     return super(ManPowerMaster, self).write(vals)

    contractor_id = fields.Many2one('res.partner','Contractor Name')
    date_join = fields.Date('Date of Joining')
    department_in_hr = fields.Many2one('hr.department','Department')
    job_id_hr = fields.Many2one('hr.job','Job Position')
    dob_id = fields.Date('Date of Birth')
    age_id = fields.Float('Age',compute="_compute_dob")
    nationality_id = fields.Many2one('res.country','Nationality')
    aadhar_id = fields.Char('Aadhar Number')
    epf_id = fields.Char('EPF UAN Number')
    esi_id = fields.Char('ESI Number')
    pf_id = fields.Char('PF Number')

    
    @api.depends('dob_id')
    def _compute_dob(self):
        for r in self:
            if r.dob_id:
                r.age_id = (datetime.now()-datetime.strptime(r.dob_id,"%Y-%m-%d")).days/356
            else:
                r.age_id = False





class manpowerYear(models.Model):
    ''' Defines an manpower year '''
    _name = "manpower.year"
    _description = "manpower Year"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help="Sequence order you want to see this year.")
    name = fields.Char('Name', required=True, help='Name of manpower year')
    code = fields.Char('Code', required=True, help='Code of manpower year')
    date_start = fields.Date('Start Date', required=True,
                             help='Starting date of manpower year')
    date_stop = fields.Date('End Date', required=True,
                            help='Ending of manpower year')
    month_ids = fields.One2many('manpower.month', 'year_id', 'Months',
                                help="related manpower months")
    grade_id = fields.Many2one('grade.master', "Grade")
    current = fields.Boolean('Current', help="Set Active Current Year")
    description = fields.Text('Description')

    @api.model
    def next_year(self, sequence):
        '''This method assign sequence to years'''
        year_id = self.search([('sequence', '>', sequence)], order='id',
                              limit=1)
        if year_id:
            return year_id.id
        return False

    
    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, ' [' + rec.code + ']' + rec.name) for rec in self]

    
    def generate_manpowermonth(self):
        interval = 1
        month_obj = self.env['manpower.month']
        for data in self:
            ds = datetime.strptime(data.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < data.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > data.date_stop:
                    de = datetime.strptime(data.date_stop, '%Y-%m-%d')
                month_obj.create({
                    'name': ds.strftime('%B'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'year_id': data.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    @api.constrains('date_start', 'date_stop')
    def _check_manpower_year(self):
        '''Method to check start date should be greater than end date
           also check that dates are not overlapped with existing manpower
           year'''
        new_start_date = datetime.strptime(self.date_start, '%Y-%m-%d')
        new_stop_date = datetime.strptime(self.date_stop, '%Y-%m-%d')
        delta = new_stop_date - new_start_date
        if delta.days > 365 and not calendar.isleap(new_start_date.year):
            raise ValidationError(_('''Error! The duration of the manpower year
                                      is invalid.'''))
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(_('''The start date of the manpower year'
                                      should be less than end date.'''))
        for old_ac in self.search([('id', 'not in', self.ids)]):
            # Check start date should be less than stop date
            if (old_ac.date_start <= self.date_start <= old_ac.date_stop or
                    old_ac.date_start <= self.date_stop <= old_ac.date_stop):
                raise ValidationError(_('''Error! You cannot define overlapping
                                          manpower years.'''))

    @api.constrains('current')
    def check_current_year(self):
        check_year = self.search([('current', '=', True)])
        if len(check_year.ids) >= 2:
            raise ValidationError(_('''Error! You cannot set two current
            year active!'''))


class ManpowerMonth(models.Model):
    ''' Defining a month of an manpower year '''
    _name = "manpower.month"
    _description = "manpower Month"
    _order = "date_start"

    name = fields.Char('Name', required=True, help='Name of manpower month')
    code = fields.Char('Code', required=True, help='Code of manpower month')
    date_start = fields.Date('Start of Period', required=True,
                             help='Starting of manpower month')
    date_stop = fields.Date('End of Period', required=True,
                            help='Ending of manpower month')
    year_id = fields.Many2one('manpower.year', 'manpower Year', required=True,
                              help="Related manpower year ")
    description = fields.Text('Description')

    _sql_constraints = [
        ('month_unique', 'unique(date_start, date_stop, year_id)',
         'manpower Month should be unique!'),
    ]

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        '''Method to check duration of date'''
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(_(''' End of Period date should be greater
                                    than Start of Peroid Date!'''))

    @api.constrains('year_id', 'date_start', 'date_stop')
    def _check_year_limit(self):
        '''Method to check year limit'''
        if self.year_id and self.date_start and self.date_stop:
            if (self.year_id.date_stop < self.date_stop or
                    self.year_id.date_stop < self.date_start or
                    self.year_id.date_start > self.date_start or
                    self.year_id.date_start > self.date_stop):
                raise ValidationError(_('''Invalid Months ! Some months overlap
                                    or the date period is not in the scope
                                    of the manpower year!'''))

    @api.constrains('date_start', 'date_stop')
    def check_months(self):
        for old_month in self.search([('id', 'not in', self.ids)]):
            # Check start date should be less than stop date
            if old_month.date_start <= \
                    self.date_start <= old_month.date_stop \
                    or old_month.date_start <= \
                    self.date_stop <= old_month.date_stop:
                    raise ValidationError(_('''Error! You cannot define
                    overlapping months!'''))

    

class Department(models.Model):
    _name = "man.department"
    _description = "Manpower Department"


class ProductTemp(models.Model):
    _inherit = 'product.template'

    length_id = fields.Float(string='Length', help="The Length in mts.")