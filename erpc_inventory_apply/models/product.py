from odoo import api, fields, models
import logging

logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # available_quantity = fields.Float(
    #     string='Free Quantity',
    #     compute='_compute_available_quantity',
    #     readonly=True,
    # )

    # @api.depends('product_variant_ids')
    # def _compute_available_quantity(self):
    #     for template in self:
    #         total_qty = 0.0
    #         warehouse = self.env.company.free_qty_warehouse
    #         logger.info(f"warehouse: {warehouse}")
    #         if warehouse:
    #             for variant in template.product_variant_ids:
    #                 quants = self.env['stock.quant'].search([
    #                     ('product_id', '=', variant.id),
    #                     ('location_id.warehouse_id', '=', warehouse.id)
    #                 ])
    #                 total_qty += sum(quants.mapped('available_quantity'))
    #         template.available_quantity = total_qty


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    available_quantity = fields.Float(
        string='Free Quantity',
        compute='_compute_available_quantity',
        readonly=True,
    )

    def _compute_available_quantity(self):
        for product in self:
            total_qty = 0.0
            warehouse = self.env.company.free_qty_warehouse
            if warehouse:

                quants = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id.warehouse_id', '=', warehouse.id)
                ])
                total_qty += sum(quants.mapped('available_quantity'))
            product.available_quantity = total_qty