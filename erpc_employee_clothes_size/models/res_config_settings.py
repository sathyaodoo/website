from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    monthly_hours = fields.Float(
        string="Monthly Working Hours",
        help="Number of working hours per year to calculate hourly cost")

    def get_values(self):
        res = super().get_values()
        monthly_hours = self.env['ir.config_parameter'].sudo().get_param('monthly_hours')
        if monthly_hours:
            res.update(monthly_hours=float(monthly_hours))
        return res

    def set_values(self):
        super().set_values()
        if self.monthly_hours:
            self.env['ir.config_parameter'].sudo().set_param('monthly_hours', self.monthly_hours)
