from odoo import models, fields, api
import re
from odoo.osv import expression


class ProductCategoryInh(models.Model):
    _inherit = 'product.category'

    advertising = fields.Boolean("Advertising Department")