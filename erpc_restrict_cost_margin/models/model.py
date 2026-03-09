from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


class ProductTemplate(models.Model):
    _inherit = "product.template"


class ProductProduct(models.Model):
    _inherit = "product.product"
