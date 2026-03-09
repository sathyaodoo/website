# from odoo import fields, models


# class ProductBrand(models.Model):
#     _inherit = 'product.brand'

#     lot_dot_discount = fields.Float("DOT Discount")

#     discount_dot_line = fields.One2many('product.brand.dot.line', 'brand_id')



# class ProductBrandDOTLines(models.Model):
#     _name = 'product.brand.dot.line'

#     lot_id = fields.Char()
#     discount_dot = fields.Float("DOT Discount")
#     brand_id = fields.Many2one('product.brand')