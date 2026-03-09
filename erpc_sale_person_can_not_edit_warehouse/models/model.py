from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    user_in_sales_group = fields.Boolean(
        string='User Belongs to Sales Group',
        compute='_compute_user_in_sales_group',

    )

    @api.depends('user_id')
    def _compute_user_in_sales_group(self):
        for order in self:
            order.user_in_sales_group = self.env.user.has_group(
                'erpc_sale_person_can_not_edit_warehouse.group_can_edit_warehouse')
