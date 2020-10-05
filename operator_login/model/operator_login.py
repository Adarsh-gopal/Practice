import base64
import logging

from odoo import api, fields, models,exceptions,_
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError, ValidationError,Warning
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class OperatorLogin(models.Model):
    _name = "operator.login"
    _inherit = ['resource.mixin']
    _description = "OperatorLogin"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('man_power', 'static/src/img', 'default_image.png')
        return (base64.b64encode(open(image_path, 'rb').read()))    

    name = fields.Many2one('man.power', 'Operator ID',domain="[('category_types','=','operator')]")
    operator_name = fields.Char(String="Operator Id",store=True,related="name.logger_id",readonly=True)
    password_id = fields.Char('Password')
    mo_id = fields.Many2one('mrp.production', 'Manufacturing Order',domain="['&',('state','!=','done'),'&',('state','!=','confirmed'),('workcenter_id','=',workcenter_id)]")
    valid_operator = fields.Boolean(string="Valid operator" ,default=False)
    shift = fields.Many2one('resource.calendar',string="Shift",domain="[('z_production_schedule','=',True)]")
    login_time = fields.Datetime('Login Time', copy=False, default=fields.Datetime.now,index=True,readonly=True)
    workcenter_id = fields.Many2one('mrp.workcenter','Machine Number')
    image = fields.Binary(
        "Photo", default=_default_image, attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,help="Small-sized photo of the employee. It is automatically resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    product_id = fields.Many2one('product.product', 'Product',related="mo_id.product_id")
    product_qty = fields.Float('Quantity To Produce',default=1.0, digits=dp.get_precision('Product Unit of Measure'),related="mo_id.product_qty")
    cutter_id = fields.Many2many('man.power',domain="[('category_types','=',('cutter','helper'))]",string="Cutterman / Helper")


    defaults = {
    'active': 1,
    'image': _default_image,
    'color': 0,
    }

    # @api.model 
    # def create(self, vals):
    #     tools.image_resize_images(vals)
    #     return super(OperatorLogin, self).create(vals)
    
     
    # def write(self, vals):
    #     tools.image_resize_images(vals) 
    #     return super(OperatorLogin, self).write(vals)



    
    def validate_operator(self):
    	for line in self:
            if line.name:
                if line.workcenter_id:
                    if line.mo_id.workcenter_id.id == line.workcenter_id.id:
                        if line.mo_id:
                            if line.shift:
                                if line.name.password_id == line.password_id:
                                #fetching manufacturing order to update shift and machine number during login
                                    mo_order = self.env['mrp.production'].search([('id', '=', line.mo_id.id)])
                                    if mo_order:
                                        op_log = self.env['operator.log']
                                        if not op_log:
                                            cutter_ids = [x.id for x in list(line.cutter_id)]
                                            vals = {
                                            'name': line.name.id,
                                            'log_id': line.mo_id.id,
                                            'shift':line.shift.id,
                                            'workcenter_id':line.workcenter_id.id,
                                            'login_time':line.login_time,
                                            'cutter_id':[(6, 0, cutter_ids)]
                                            }
                                            log_obj = self.env['operator.log'].create(vals)
                                        for mo_line in mo_order:
                                            mo_line.update({'operator_name':line.name.id,
                                                'logger_name':line.name.logger_id,
                                                'shift':line.shift.id,
                                                'cutter_id':[(6, 0, cutter_ids)]})
                                        line.valid_operator = True
                                else:
                                    raise exceptions.Warning(("Please enter valid password"))
                            else:
                                raise exceptions.Warning(("Select the shift"))
                        else:
                            raise exceptions.Warning(("Select Manufacturing Order"))
                else:
                    raise exceptions.Warning(("Select Machine Number"))
            else:
                raise exceptions.Warning(("Select the Operator name"))
        
