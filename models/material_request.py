# -*- coding: utf - 8 - *-

from odoo import models, fields, api
from datetime import timedelta


class MaterialRequest(models.Model):
    _name = 'material.request'
    _description = 'Material Request'

    _rec_name = 'ref'
    ref = fields.Char(
        default='New',
        readonly=1
    )

    request_date = fields.Date(
        string='Request Date',
        required=True
    )
    department_id = fields.Many2one(
        'hr.department', string='Department',
        required=True
    )
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    operation_type_id = fields.Many2one(
        'stock.picking.type',
        string='Operation Type',
        required=True,
        domain=[('code', '=', 'internal')]
    )
    destination_id = fields.Many2one(
        'stock.location',
        string='Destination',
        required=True,
        # domain=[('usage', '=', 'internal')]
    )

    source_id = fields.Many2one(
        'stock.location',
        string='Source',
        required=True,
        # domain=[('usage', '=', 'internal')]
    )

    material_request_line_ids = fields.One2many(
        'material.request.line',
        'material_request_id',
        string='Material Request Lines',
        required=True
    )

    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('canceled', 'Canceled'),
        ],
        default='draft'
    )

    all_available = fields.Boolean(default=False)
    all_transferred = fields.Boolean(default=False)
    all_purchased = fields.Boolean(default=False)

    def action_confirm(self):
        for rec in self:
            rec.state = "pending"
            # rec.action_check_availability()

    def action_in_progress(self):
        for rec in self:
            rec.state = "in_progress"

    def action_done(self):
        for rec in self:
            rec.state = "done"

    def action_canceled(self):
        for rec in self:
            rec.state = "canceled"

    def action_check_availability(self):
        for rec in self:
            available = 0
            for pro in rec.material_request_line_ids:
                if pro.quantity <= pro.product_id.qty_available:
                    pro.is_available = True
                if pro.is_available:
                    available += 1
            if (available == len(rec.material_request_line_ids)):
                rec.all_available = True

    def action_open_transferred(self):
        action = self.env['ir.actions.actions']._for_xml_id('stock.action_picking_tree_internal')
        action['domain'] = [('origin', '=', self.ref)]
        return action

    def action_open_purchased(self):
        action = self.env['ir.actions.actions']._for_xml_id('purchase.purchase_rfq')
        action['domain'] = [('origin', '=', self.ref)]
        return action

    def action_create_transferred(self):
        self.ensure_one()
        transferred = 0
        move_vals = []
        for line in self.material_request_line_ids:
            if (line.is_available and not (line.transferred)):
                line.transferred = True
                move_vals.append({
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': self.source_id.id,
                    'location_dest_id': self.destination_id.id,
                    'date': self.request_date,
                    'date_deadline': self.request_date,
                })
            if (line.transferred):
                transferred += 1

        if (transferred == len(self.material_request_line_ids)):
            self.all_transferred = True

        if len(move_vals) == 0:
            return

        move_ids = self.env['stock.move'].create(move_vals)

        self.env['stock.picking'].create({
            'picking_type_id': self.operation_type_id.id,
            'location_id': self.source_id.id,
            'location_dest_id': self.destination_id.id,
            'move_ids_without_package': [(6, 0, move_ids.ids)],  # Using tuple format
            'partner_id': self.env.uid,  # Assuming partner_id is required
            'origin': self.ref,
        })

    def action_create_purchase(self):
        self.ensure_one()
        self.action_check_availability()
        purchased = 0
        if (self.all_available):
            return
        purchase_vals = []
        for line in self.material_request_line_ids:
            if not (line.is_available) and not line.purchased:
                line.purchased = True
                purchase_vals.append({
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': self.source_id.id,
                    'location_dest_id': self.destination_id.id,
                    'date': self.request_date,
                    'date_deadline': self.request_date,
                })
            if line.purchased or line.is_available:
                purchased += 1
        if (purchased == len(self.material_request_line_ids)):
            self.all_purchased = True
        if len(purchase_vals) == 0:
            return
        purchase_ids = self.env['stock.move'].create(purchase_vals)
        self.env['purchase.order'].create({
            'partner_id': self.vendor_id.id,
            'currency_id': self.env.ref('base.JOD').id,
            'date_order': fields.Datetime.now(),
            'date_planned': fields.Datetime.now() + timedelta(days=1),
            'picking_type_id': self.operation_type_id.id,
            'order_line': [(0, 0, {  # Assuming order_line refers to purchase.order.line fields
                'product_id': line.product_id.id,
                'product_qty': line.product_uom_qty - line.product_id.qty_available,
                'price_unit': line.product_id.standard_price,  # Example of setting price
                'date_planned': fields.Datetime.now(),
                'name': line.product_id.name,
                'product_uom': line.product_id.uom_id.id,
            }) for line in purchase_ids],
            'origin': self.ref
        })

    @api.model
    def create(self, vals):
        res = super(MaterialRequest, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('material_req_seq')
        return res


class MaterialRequestLine(models.Model):
    _name = 'material.request.line'

    material_request_id = fields.Many2one('material.request', string='Material Request')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    is_available = fields.Boolean(string='Is Available')
    purchased = fields.Boolean(string='Purchased')
    transferred = fields.Boolean(string='Transferred')
