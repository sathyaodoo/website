from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    show_available_qty = fields.Integer("Show Available Qty")
    discount_percent = fields.Float("Discount %")