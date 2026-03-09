from odoo import api, fields, models

class Company(models.Model):
    _inherit = "res.company"

    free_qty_warehouse = fields.Many2one('stock.warehouse', domain= "[('company_id', '=', id)]", readonly=False, string='Free Quantity Warehouse')
