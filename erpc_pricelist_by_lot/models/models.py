from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import logging

_log = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    restrict_lot_in_sale_order = fields.Boolean(
        string='Restrict Lot in Sale Order',
        help='If enabled, products in this category cannot have a lot set in sale orders.'
    )


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    lot_id = fields.Many2one('stock.lot', string='Lot')
    final_price = fields.Monetary(string="Final Price", compute="_compute_final_price", store=True)

    @api.depends('compute_price', 'fixed_price', 'percent_price', 'product_tmpl_id.list_price')
    def _compute_final_price(self):
        for record in self:
            if record.compute_price == 'fixed':
                record.final_price = record.fixed_price
            elif record.compute_price == 'percentage':
                if record.product_tmpl_id:
                    discount = (record.percent_price / 100.0) * record.product_tmpl_id.list_price
                    record.final_price = record.product_tmpl_id.list_price - discount
                else:
                    record.final_price = 0.0  
            else:
                record.final_price = 0.0  

#TODO: To uncomment after adding industry_fsm_stock in the manifest

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'

#     @api.depends('product_id', 'product_uom_id', 'product_uom_qty', 'fsm_lot_id')
#     def _compute_pricelist_item_id(self):
#         for line in self:
#             # Custom logic applies only if fsm_lot_id is set
#             if line.fsm_lot_id:
#                 pricelist = line.order_id.pricelist_id
#                 if not line.product_id or line.display_type or not pricelist:
#                     line.pricelist_item_id = False
#                     continue

#                 matching_items = pricelist.item_ids.filtered(
#                     lambda item: item.fsm_lot_id == line.fsm_lot_id
#                 )
#                 if not matching_items:
#                     matching_items = pricelist.item_ids.filtered(
#                         lambda item: not item.fsm_lot_id
#                     )

#                 # Initialize the best item
#                 best_item = None
#                 highest_price = 0.0
#                 for item in matching_items:
#                     # Check matching conditions
#                     if item.product_id and item.product_id != line.product_id:
#                         continue
#                     if item.product_tmpl_id and item.product_tmpl_id != line.product_id.product_tmpl_id:
#                         continue
#                     if item.categ_id and item.categ_id != line.product_id.categ_id:
#                         continue
#                     if item.min_quantity and item.min_quantity > line.product_uom_qty:
#                         continue

#                     # Calculate the price for the current item
#                     price = item._compute_price(
#                         line.product_id,
#                         line.product_uom_qty,
#                         line.product_uom,
#                         line.order_id.date_order,
#                         pricelist.currency_id,
#                     )

#                     # Update the best item if the price is higher
#                     if price > highest_price:
#                         best_item = item
#                         highest_price = price

#                 line.pricelist_item_id = best_item
#             else:
#                 # Call the super method (default Odoo logic) if no fsm_lot_id is set
#                 super(SaleOrderLine, line)._compute_pricelist_item_id()

#     @api.onchange('fsm_lot_id', 'product_id')
#     def _onchange_lot_id(self):
#         if self.fsm_lot_id and self.product_id.categ_id.restrict_lot_in_sale_order:
#             raise ValidationError(_(
#                 "You cannot set a lot for the product '%s' as its category '%s' restricts lot usage in sale orders."
#             ) % (self.product_id.display_name, self.product_id.categ_id.display_name))
#         self._compute_price_unit()
#         self._compute_discount()