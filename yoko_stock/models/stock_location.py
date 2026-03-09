from odoo import fields, models, api
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_main_location = fields.Boolean(string="Is a Main Location?", default=False)

    @api.constrains('is_main_location')
    def _check_main_location(self):
        if not self.is_main_location:
            return
        if len(self.env['stock.location'].search([('is_main_location', '=', True)])) > 1:
            raise ValidationError("There is an existing Main Location")
