from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    can_edit_prices = fields.Boolean(
        string='Can Edit Prices',
        compute='_compute_can_edit_prices',
        store=False,
        help="Automatically True if user has Edit SO Price Unit group"
    )

    @api.depends()
    def _compute_can_edit_prices(self):
        has_group = self.env.user.has_group('erpc_restric_unit_price.group_can_edit_so_price_unit')
        for order in self:
            order.can_edit_prices = has_group