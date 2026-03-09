from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    driver_id = fields.Many2one('res.partner', string='Driver', store=True,
                                domain="[('is_driver', '=', True), ('driver_state', '=', 'active')]", tracking=True,
                                compute="_compute_driver_id")


    @api.depends('picking_ids', 'picking_ids.driver_id')
    def _compute_driver_id(self):
        for picking in self:
            if picking.picking_ids:
                picking.driver_id = picking.picking_ids.driver_id
            else:
                picking.driver_id = False


class StockPicking(models.Model):
    _inherit = "stock.picking"
