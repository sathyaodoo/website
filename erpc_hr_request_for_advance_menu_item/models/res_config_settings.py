from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ceiling_limit_for_short_advance = fields.Integer(
        string="Ceiling Limit for Short Advance",
        related="company_id.ceiling_limit_for_short_advance",
        readonly=False,
    )

    ceiling_limit_for_long_advance = fields.Integer(
        string="Ceiling Limit for Long Advance",
        related="company_id.ceiling_limit_for_long_advance",
        readonly=False,
    )
