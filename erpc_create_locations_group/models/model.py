from odoo import api, fields, models
from odoo import exceptions


class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('erpc_create_locations_group.group_create_location'):
            raise exceptions.AccessError("You do not have permission to create locations.")
        return super(StockLocationInherit, self).create(vals)

    def write(self, vals):
        if not self.env.user.has_group('erpc_create_locations_group.group_create_location'):
            raise exceptions.AccessError("You do not have permission to edit locations.")
        return super(StockLocationInherit, self).write(vals)

    def unlink(self):
        if not self.env.user.has_group('erpc_create_locations_group.group_create_location'):
            raise exceptions.AccessError("You do not have permission to delete locations.")
        return super(StockLocationInherit, self).unlink()

    # The commented below shall be removed after checking with AliAyyad
    # @api.model
    # def archive(self, vals):
    #     if not self.env.user.has_group('erpc_create_locations_group.group_create_location'):
    #         raise exceptions.AccessError("You do not have permission to archive locations.")
    #     return super(StockLocationInherit, self).archive(vals)

    def export_data(self, fields_to_export):
        if not self.env.user.has_group('erpc_create_locations_group.group_create_location'):
            raise exceptions.AccessError("You do not have permission to export locations.")
        return super(StockLocationInherit, self).export_data(fields_to_export)

