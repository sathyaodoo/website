# from odoo import fields, models, api


# class ProductTemplate(models.Model):
#     _inherit = 'product.template'

#     dot_price = fields.Float("DOT Price", compute="_compute_dot_price", store=True)

#     @api.depends('brand_id.lot_dot_discount', 'list_price')
#     def _compute_dot_price(self):
#         for rec in self:
#             rec.dot_price = rec.list_price - (rec.list_price * (rec.brand_id.lot_dot_discount / 100))
