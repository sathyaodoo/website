from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def copy_data(self, default=None):
        if not self.env.user.has_group('erpc_inventory_hide_duplicate.group_hide_duplicate'):
            raise ValidationError(_('You do not have the necessary access rights to duplicate this record, please create a new one.'))
        return super().copy_data(default)

