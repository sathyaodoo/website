from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_expenses_categ = fields.Boolean(string="Is Expenses")