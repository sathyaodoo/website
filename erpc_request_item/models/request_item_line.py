from odoo import models, fields, api


class RequestItemLine(models.Model):
    _name = 'request.item.line'

    product_id = fields.Many2one('product.product', string='Product')
    request_id = fields.Many2one('request.item')
    lot_id = fields.Many2one('stock.lot', "Lot")
    product_uom_qty = fields.Float('Qty Requested')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
