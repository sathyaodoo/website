from odoo import api, fields, models, exceptions
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line', 'order_line.product_id', 'order_line.product_id.detailed_type')
    def _check_your_field(self):
        for order in self:
            for line in order.order_line:
                if line.product_id.tracking == 'lot' and not line.lot_id:
                    raise ValidationError(f"The lot is required for product: {line.product_id.name}.")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_id = fields.Many2one(
        "stock.lot",
        "Lot",
        compute="_compute_lot_id",
        store=True,
        readonly=False,
    )

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id=group_id)
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    @api.depends("product_id")
    def _compute_lot_id(self):
        for sol in self:
            if sol.product_id != sol.lot_id.product_id:
                sol.lot_id = False
