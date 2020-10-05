# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

#Inspection Plan
class InspectionPlan(models.Model):
    _name = "inspection.plan"
    _inherit = ['mail.thread']
    _description = "Inspection Plan"

    name = fields.Char()
    product_tmpl_id = fields.Many2one('product.template')
    product_id = fields.Many2one('product.product',domain="[('product_tmpl_id', '=', product_tmpl_id)]")
    picking_type_id = fields.Many2one('stock.picking.type')
    team_id = fields.Many2one('quality.alert.team')

    quality_point_ids = fields.One2many('quality.point','inspection_plan_id')

    @api.model
    def create(self,vals):
        sequence = self.env['stock.picking.type'].browse(vals.get('picking_type_id')).sequence_for_inspection_plan
        vals['name'] = sequence.next_by_id()
        return super(InspectionPlan,self).create(vals)

    start_date = fields.Date()
    end_date = fields.Date()

    @api.constrains('start_date','end_date')
    def _check_quantities(self):
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError(_("""End Date Can not be less than Start Date"""))




# Quality Point
class QualityPoint(models.Model):
    _inherit = "quality.point"

    inspection_plan_id = fields.Many2one('inspection.plan', ondelete='cascade')
    team_id = fields.Many2one(
        'quality.alert.team', 'Team', check_company=True,
        default=False, required=False,
        compute='_compute_details',store=True)
    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
        compute='_compute_details',store=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product', required=False, check_company=True,
        domain="[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute='_compute_details',store=True)
    picking_type_id = fields.Many2one('stock.picking.type', "Operation Type", required=False, check_company=True,
        compute='_compute_details',store=True)

    @api.depends('inspection_plan_id','inspection_plan_id.product_tmpl_id','inspection_plan_id.picking_type_id','inspection_plan_id.team_id')
    def _compute_details(self):
        for rec in self:
            if rec.inspection_plan_id:
                rec.product_id = rec.inspection_plan_id.product_id
                rec.product_tmpl_id = rec.inspection_plan_id.product_tmpl_id.id
                rec.picking_type_id = rec.inspection_plan_id.picking_type_id.id
                rec.team_id = rec.inspection_plan_id.team_id.id
            else:
                rec.product_tmpl_id = rec.picking_type_id = rec.team_id = False

    test_method_id = fields.Many2one('quality.test.method')

    characteristic = fields.Many2one('quality.characteristic')

    @api.onchange('characteristic')
    def _set_title(self):
        self.title = self.characteristic.description








#Inspection Sheet
class InspectionSheet(models.Model):
    _name = "inspection.sheet"
    _inherit = ['mail.thread']
    _description = "Inspection Sheet"

    name = fields.Char()
    
    source = fields.Char(related='picking_id.origin')
    product_id = fields.Many2one('product.product')
    picking_id = fields.Many2one('stock.picking')
    lot_id = fields.Many2one('stock.production.lot')
    team_id = fields.Many2one('quality.alert.team')
    company_id = fields.Many2one('res.company')


    quality_check_ids = fields.One2many('quality.check','inspection_sheet_id')

    
    date = fields.Date(default=fields.Date.today())
    quantity_recieved = fields.Float(compute='_compute_details')
    quantity_accepted = fields.Float()
    quantity_rejected = fields.Float()
    quantity_destructive = fields.Float()
    under_deviation = fields.Float()

    @api.depends('picking_id','picking_id.move_ids_without_package','picking_id.move_ids_without_package.product_uom_qty')
    def _compute_details(self):
        for rec in self:
            rec.quantity_recieved = rec.picking_id.move_ids_without_package.filtered(lambda line: line.product_id == rec.product_id).product_uom_qty

    status = fields.Selection([('open','Open'),
                            ('accept','Accept'),
                            ('reject','Reject'),
                            ('acceptud','Accepted Under Deviation')],default='open')
    state = fields.Selection([('open','Open'),
                            ('accept','Accepted'),
                            ('reject','Rejected')],default='open')

    def state_approve(self):
        if self.env.user.id == self.team_id.approver_id.id:
            self.state = 'accept'
        else:
            raise UserError(_("""OOPS!!!\nLooks like you aren't authorized to Accept"""))
        if self.quantity_accepted + self.quantity_rejected + self.quantity_destructive + self.under_deviation != self.quantity_recieved:
            raise ValidationError(_("""Sum of Quantities Accepeted, Rejected, Destructive and Deviation "MUST" be same as Recieved Quantity"""))

    def state_reject(self):
        if self.env.user.id == self.team_id.approver_id.id:
            self.state = 'reject'
        else:
            raise UserError(_("""OOPS!!!\nLooks like you aren't authorized to Reject"""))
        if self.quantity_accepted + self.quantity_rejected + self.quantity_destructive + self.under_deviation != self.quantity_recieved:
            raise ValidationError(_("""Sum of Quantities Accepeted, Rejected, Destructive and Deviation "MUST" be same as Recieved Quantity"""))


    @api.model
    def create(self,vals):
        sequence = self.env['stock.picking'].browse(vals.get('picking_id')).picking_type_id.sequence_for_inspection_sheet
        vals['name'] = sequence.next_by_id()
        return super(InspectionSheet,self).create(vals)

    def process_quantities(self):
        self.picking_id.move_line_nosuggest_ids = [(0,0,{
            'product_id':self.product_id.id,
            'location_dest_id':self.picking_id.location_dest_id.id,
            'qty_done':self.quantity_accepted+self.under_deviation,
            'product_uom_id':self.product_id.product_tmpl_id.uom_id.id,
            'location_id':self.picking_id.location_id.id
            })]
        self.picking_id.move_line_nosuggest_ids = [(0,0,{
            'product_id':self.product_id.id,
            'location_dest_id':self.picking_id.location_dest_id.id,
            'qty_done':self.quantity_rejected,
            'product_uom_id':self.product_id.product_tmpl_id.uom_id.id,
            'location_id':self.picking_id.location_id.id
            })]
        self.picking_id.move_line_nosuggest_ids = [(0,0,{
            'product_id':self.product_id.id,
            'location_dest_id':self.env['stock.location'].search([('desctructive_location','=',True)]).id,
            'qty_done':self.quantity_destructive,
            'product_uom_id':self.product_id.product_tmpl_id.uom_id.id,
            'location_id':self.picking_id.location_id.id
            })]


#Desctructive Location
class StockLocation(models.Model):
    _inherit = 'stock.location'

    desctructive_location = fields.Boolean('Is a Desctructive Location?')

    @api.onchange('desctructive_location')
    def _check_one(self):
        if self.desctructive_location == True:
            if len(self.env['stock.location'].search([('desctructive_location','=',True)])):
                self.desctructive_location = False
                raise ValidationError(_("""Can not have more than one destructive location"""))



# Quality Check
class QualityCheck(models.Model):
    _inherit = "quality.check"

    inspection_sheet_id = fields.Many2one('inspection.sheet',compute='_get_inspection_sheet', store=True, ondelete='cascade')


    @api.depends('product_id','picking_id','lot_id')
    def _get_inspection_sheet(self):
        for rec in self:
            if rec.picking_id:
                sheet = self.env['inspection.sheet'].search([('product_id','=',rec.product_id.id),
                                                            ('picking_id','=',rec.picking_id.id),
                                                            ('lot_id','=',rec.lot_id.id),
                                                            ('team_id','=',rec.team_id.id,),
                                                            ('company_id','=',rec.company_id.id)],limit=1).id
                if sheet:
                    rec.inspection_sheet_id = sheet
                else:
                    sheet = self.env['inspection.sheet'].create({'product_id':rec.product_id.id,
                                                                'picking_id':rec.picking_id.id,
                                                                'lot_id':rec.lot_id.id,
                                                                'team_id':rec.team_id.id,
                                                                'company_id':rec.company_id.id}).id
                    rec.inspection_sheet_id = sheet


    norm = fields.Float(related="point_id.norm")
    tolerance_min = fields.Float(related="point_id.tolerance_min")
    tolerance_max = fields.Float(related="point_id.tolerance_max")
    norm_unit = fields.Char(related="point_id.norm_unit")
    test_method_id = fields.Many2one('quality.test.method',related="point_id.test_method_id")


    quality_state = fields.Selection([
        ('none', 'To do'),
        ('pass', 'Passed'),
        ('fail', 'Failed')], string='Status', tracking=True,
        default='none', copy=False, store=True, compute='_set_state')


    @api.depends('test_type','measure')
    def _set_state(self):
        for rec in self:
            if rec.test_type == 'measure':
                if rec.measure >= rec.tolerance_min and rec.measure <= rec.tolerance_max:
                    rec.quality_state = 'pass'
                else:
                    rec.quality_state = 'fail'
            else:
                rec.quality_state = rec.quality_state



class QualityTestMethod(models.Model):
    _name = "quality.test.method"
    _description = "Quality Test Method"

    name = fields.Char(string="Test Method")


class QualityAlertTeam(models.Model):
    _inherit = 'quality.alert.team'

    approver_id = fields.Many2one('res.users')


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    sequence_for_inspection_plan = fields.Many2one('ir.sequence')
    sequence_for_inspection_sheet = fields.Many2one('ir.sequence')


#Quality Characteristics
class QualityCharacteristic(models.Model):
    _name = 'quality.characteristic'
    _description = 'QualityCharacteristic'

    name = fields.Char()
    description = fields.Char()


class QualityAlertTeam(models.Model):
    _inherit = 'quality.alert.team'

    inspection_sheet_count = fields.Integer('# Inspection Sheet Alerts', compute='_compute_inspection_sheet_count')

    def _compute_inspection_sheet_count(self):
        sheet_data = self.env['inspection.sheet'].read_group([('team_id', 'in', self.ids), ('state', '=', 'open')], ['team_id'], ['team_id'])
        sheet_result = dict((data['team_id'][0], data['team_id_count']) for data in sheet_data)
        for team in self:
            team.inspection_sheet_count = sheet_result.get(team.id, 0)