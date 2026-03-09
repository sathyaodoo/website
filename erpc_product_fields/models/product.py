from odoo import fields, models, api, _
import logging

logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # oem_cca = fields.Char(string="OEM&CCA")

    available_quantity = fields.Float(
        string="Free Quantity",
        digits=(16, 0),
        compute="_compute_available_quantity",
        readonly=True,
    )
