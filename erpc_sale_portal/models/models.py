from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError, UserError, AccessError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    client_update = fields.Selection([('accepted', 'Accepted'), ('declined', 'Declined')])
    decline_reason = fields.Text()

    # def write(self, vals):
    #     if self.env['sale.order'].user in (sales_team.group_sale_salesman) and 'state' '=' 'sales' :
    #         raise UserError(
    #             '')

    # def write(self, vals):
    #     user_groups = self.env.user.groups_id
    #     if any(group.id == self.env.ref('sales_team.group_sale_salesman').id for group in user_groups):
    #         if vals.get('state') == 'sales':
    #             raise UserError('You are not allowed to change the state to "sales" while being a Salesman.')
    #     return super(SaleOrder , self).write(vals)

    # def write(self, vals):
    #     if self.env.user.user_has_groups(
    #             'sales_team.group_sale_salesman') and self.state == "sale":
    #         raise UserError(
    #             'You are not allowed to change SO if it is already posted.')
    #     return super().write(vals)

    def write(self, vals):
        if self.env.user.has_group(
                'sales_team.group_sale_salesman') and not self.env.user.has_group(
            'yoko_customization.confirm_so') and self.state == "sale":
            raise UserError(
                'You are not allowed to change SO if it is already posted.')
        return super().write(vals)
