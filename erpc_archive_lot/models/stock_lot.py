from odoo import models, fields, api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    active = fields.Boolean(string="Active", default=True, help="Set active to false to hide the lot without removing it.")

    def archive_lot(self):
        """Archive the lot by setting active to False"""
        return self.write({'active': False})

    def unarchive_lot(self):
        """Unarchive the lot by setting active to True"""
        return self.write({'active': True})