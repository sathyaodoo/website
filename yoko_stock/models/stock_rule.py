from odoo import fields, models, api
import logging


class StockRule(models.Model):
    _inherit = "stock.rule"


    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        res = super(StockRule, self)._get_stock_move_values(
        product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        if values.get('aditional_note', False):
            res['aditional_note'] = values.get('aditional_note')
        return res