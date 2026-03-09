from odoo import models
import logging

_logger = logging.getLogger(__name__)

class StockForecasted(models.AbstractModel):
    _inherit = 'stock.forecasted_product_product'

    def _get_product_remaining_confirmed_qty(self, product_id):
        _logger.info(f"\n\n\\n\n\\n\n\n\n\n product_id {product_id}")
        requisition_lines = self.env['purchase.requisition.line'].search([
            ('product_id.id', 'in', product_id),
            ('requisition_id.state', '=', 'ongoing'),
        ])
        return sum(requisition_lines.mapped('remaining_ordered_quantity'))

    def _get_template_remaining_confirmed_qty(self, product_template_id):
        _logger.info(f"\n\n\\n\n\\n\n\n\n\n product_template_id {product_template_id}")
        products = self.env['product.product'].search([('product_tmpl_id', '=', product_template_id)])
        requisition_lines = self.env['purchase.requisition.line'].search([
            ('product_id.id', 'in', products.ids),
            ('requisition_id.state', '=', 'ongoing'),
        ])
        return sum(requisition_lines.mapped('remaining_ordered_quantity'))

    def _get_report_header(self, product_template_ids, product_ids, wh_location_ids):
        res = super(StockForecasted, self)._get_report_header(product_template_ids, product_ids, wh_location_ids)
        
        if product_ids:
            confirmed_qty = self._get_product_remaining_confirmed_qty(product_ids)
            res['remaining_ordered_quantity'] = confirmed_qty

        if product_template_ids:
            template_confirmed_qty = sum(self._get_template_remaining_confirmed_qty(template_id) for template_id in product_template_ids)
            res['remaining_ordered_quantity'] = template_confirmed_qty
        
        return res
