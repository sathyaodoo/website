from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    free_qty_warehouse = fields.Many2one(related="company_id.free_qty_warehouse",domain="[('company_id', '=', company_id)]", readonly=False)
