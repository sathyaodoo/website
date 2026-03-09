from odoo import fields, models, api


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    mrp_production_ids = fields.Many2many(
        'mrp.production', string='Manufacturing order',
        copy=False, states={'done': [('readonly', True)]},
        groups='stock.group_stock_manager, erpc_landed_cost_create.group_landed_cost_button')
