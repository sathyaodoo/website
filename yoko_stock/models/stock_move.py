from odoo import fields, models, api
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    aditional_note = fields.Text(string='Add. Note')
