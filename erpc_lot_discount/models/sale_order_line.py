# from odoo import api, fields, models, _
# import logging

# _logger = logging.getLogger(__name__)


# class SaleOrderLineInherit(models.Model):
#     _inherit = "sale.order.line"

#     is_lot_dot = fields.Boolean("Is DOT", related="lot_id.is_dot")
#     offer_discount = fields.Float("Offer Discount", compute="_compute_offer_discount")
#     offer_id  = fields.Many2one(
#         comodel_name='product.offer',compute="_compute_offer_discount",
#         string='Offer',
#         required=False, store=True)
#     lot_dot_discount = fields.Float("DOT Discount", compute="_compute_lot_dot_discount")

#     @api.depends('product_id', 'lot_id')
#     def _compute_lot_dot_discount(self):
#         for rec in self:
#             rec.lot_dot_discount = 0
#             if rec.product_id and rec.product_id.brand_id and rec.is_lot_dot:
#                 related_dot_line = self.env['product.brand.dot.line'].search([
#                     ('lot_id', '=', rec.lot_id.name),
#                     ('brand_id', '=', rec.product_id.brand_id.id)])

#                 if related_dot_line:
#                     rec.lot_dot_discount = related_dot_line[0].discount_dot

#                 else:
#                     rec.lot_dot_discount = rec.product_id.brand_id.lot_dot_discount


#     @api.depends('product_id', 'lot_id', 'order_id.partner_id')
#     def _compute_offer_discount(self):
#         for rec in self:
#             rec.offer_discount = 0
#             if rec.product_id:
#                 partner_offer_ids = rec.order_id.partner_id.sudo().offer_ids.filtered(lambda offer: offer.brand_id.id == rec.product_template_id.brand_id.id)
#                 if partner_offer_ids:
#                     offer_id = partner_offer_ids.mapped('offer_line_ids').filtered(lambda line: line.product_id.id == rec.product_template_id.id)
#                     if offer_id:
#                         rec.offer_id = offer_id[0].offer_id.id
#                         rec.offer_discount = offer_id[0].discount  # in case there are multiple offers for the same product/partner


#     # @api.onchange('product_id', 'lot_id')
#     # def product_id_change_offer_diiscount(self):
#     #     self.discount = self.offer_discount

#     #     if self.is_lot_dot:
#     #         discount_price_without_dot = self.price_unit - (self.price_unit * (self.discount / 100))
#     #         discount_price_with_dot = discount_price_without_dot - (discount_price_without_dot * (self.lot_dot_discount / 100))
#     #         self.discount = (((self.price_unit - discount_price_with_dot) * 100) / self.price_unit) if self.price_unit != 0 else 0

