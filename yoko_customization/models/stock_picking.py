# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # sale_id = fields.Many2one('sale.order', string='Sale Order', compute='_compute_sale_id', store=True)
    driver_id = fields.Many2one('res.partner', string='Driver', domain="[('is_driver', '=', True)]", tracking=True)
    # TODO GR: to add outgoing_driver_id and compute method in another module bc it takes long loading time
    # outgoing_driver_id = fields.Many2one(
    #     'res.partner',
    #     string="Outgoing Driver",
    #     compute="_compute_outgoing_driver",
    #     store=True
    # )
    # collector = fields.Many2one('res.partner', string='Collector', related='sale_id.invoice_ids.collector', domain="[('is_driver', '=', False)]", tracking=True)
    location_id = fields.Many2one(domain="[('usage', 'not in', ['view'])]")
    location_dest_id = fields.Many2one(domain="[('usage', 'not in', ['view'])]")

    # def _compute_sale_id(self):
    #     for line in self:
    #         sale_id = self.env['sale.order'].search([('name', '=', line.origin)])
    #         if sale_id:
    #             line.sale_id = sale_id.id
    #         else:
    #             line.sale_id = False

    # @api.depends('picking_type_code', 'group_id', 'group_id.stock_move_ids.picking_id.driver_id')
    # def _compute_outgoing_driver(self):
    #     for picking in self:
    #         if picking.picking_type_code == 'outgoing' and picking.group_id:
    #             internal_picking = self.search([
    #                 ('group_id', '=', picking.group_id.id),
    #                 ('picking_type_code', '=', 'internal')
    #             ], limit=1)
    #
    #             picking.outgoing_driver_id = internal_picking.driver_id
    #         else:
    #             picking.outgoing_driver_id = False

    def button_validate(self):
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        for picking in self:
            if picking.picking_type_id and picking.picking_type_id.code == 'outgoing':
                for line in picking.move_line_ids:
                    if line.picked > line.quantity_product_uom:
                        raise ValidationError("Quantity exceeds the Sales Order Quantity")

        res = super(StockPicking, self).button_validate()

        return res
