from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    lot_promotion = fields.Float("Lot Discount")


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def write(self, vals):  # Overrides the 'write' method for updating records
        # Check if the current user belongs to the allowed group
        if not self.env.user.has_group('erpc_lot_discount.group_allow_pricelist_edit'):
            raise UserError(_("You are not allowed to modify this record.\nGroup Allow Pricelists Edit"))
        return super().write(vals)  # Call original 'write' if allowed

    @api.model
    def create(self, vals):  # Overrides the 'create' method for new records
        # Check if the current user belongs to the allowed group
        if not self.env.user.has_group('erpc_lot_discount.group_allow_pricelist_edit'):
            raise UserError(_("You are not allowed to create new records.\nGroup Allow Pricelists Edit"))
        return super().create(vals)
