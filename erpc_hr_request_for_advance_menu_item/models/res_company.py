from odoo import models, fields, api


class CompanyReport(models.Model):
    _inherit = "res.company"

    ceiling_limit_for_short_advance = fields.Integer(
        string="Ceiling Limit for Short Advance",
    )

    ceiling_limit_for_long_advance = fields.Integer(
        string="Ceiling Limit for Long Advance",
    )
