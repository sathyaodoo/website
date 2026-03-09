from odoo import api, fields, models
from datetime import datetime, time
import logging

_logger = logging.getLogger(__name__)


class BrandTarget(models.Model):
    _name = 'brand.target'
    _description = 'Brand Target Table'

    product_brand = fields.Many2one('product.category', string="Brand", required=True)
    month = fields.Selection(
        [(str(m), datetime(2000, m, 1).strftime("%B")) for m in range(1, 13)],
        string="Month",
    )

    year = fields.Selection(
        [
            (str(year), str(year))
            for year in range(datetime.today().year - 20, datetime.today().year + 21)
        ],
        string="Year",
        default=lambda self: str(datetime.today().year),
    )

    target_qty = fields.Integer(string="Target Qty")
    target_value = fields.Float(string="Target $")
    target_percentage = fields.Float(string="Seasonal Coefficent")
