from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_demand = fields.Float(compute='_compute_total_demand', store=True)
    total_done = fields.Float(compute='_compute_total_done', store=True)

    @api.depends('move_ids.product_uom_qty', 'move_ids.quantity')
    def _compute_total_demand(self):
        for record in self:
            record.total_demand = sum(record.move_ids.mapped('product_uom_qty'))

    @api.depends('move_ids.quantity')
    def _compute_total_done(self):
        for record in self:
            record.total_done = sum(record.move_ids.mapped('quantity'))


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_quantity = fields.Float(compute='_compute_total_quantity', store=True)

    @api.depends('order_line.product_qty')
    def _compute_total_quantity(self):
        for record in self:
            record.total_quantity = sum(record.order_line.mapped('product_qty'))