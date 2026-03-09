from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        allowed_fields_for_others = {'note', 'picking_readiness'}
        # allowed_fields_for_others = {'note', 'picking_readiness', 'state'}
        for order in self:
            if self.env.user.has_group('erpc_sale_quotation_restriction.group_so_edit_own'):
                if order.create_uid != self.env.user:
                    disallowed_fields = set(vals.keys()) - allowed_fields_for_others
                    if disallowed_fields:
                        raise ValidationError(_("You can only edit your own quotations, except for fields: %s.") % ', '.join(allowed_fields_for_others))
        return super(SaleOrder, self).write(vals)
