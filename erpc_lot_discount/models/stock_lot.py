from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    is_dot = fields.Boolean(string="Is DOT", default=False)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    is_lot_dot = fields.Boolean(string="Is DOT", related="lot_id.is_dot")
