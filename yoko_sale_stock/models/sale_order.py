from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_default_is_promo(self):
        if self.env.user.has_group('yoko_security_custom.advertising_department'):
            return True
        return False

    is_promo = fields.Boolean(string='Is Promotional', default=_get_default_is_promo,
                              help='If True, means it comes from a Promotional Team')

    def write(self, vals):
        if not self.env.is_superuser() and not self.env.user.has_group('yoko_security_custom.advertising_department') \
                and any(rec.is_promo for rec in self):
            if len(self) > 1:
                raise UserError("You are not allowed to edit Promotional Sale Orders.")
            else:
                raise UserError("%s is a Promotional Order, You are not allowed to edit it." % self.name)
        if (self.env.user.has_group("yoko_security_custom.indoor") or self.env.user.has_group(
                "erpc_type_quotation.group_corporate")) and any(pick.priority == '1' for pick in self.picking_ids):
            raise UserError("SO has starred Picking, You are not allowed to edit it")
        return super(SaleOrder, self).write(vals)

    def unlink(self):
        if not self.env.is_superuser() and not self.env.user.has_group('yoko_security_custom.advertising_department') \
                and any(rec.is_promo for rec in self):
            if len(self) > 1:
                raise UserError("You are not allowed to delete Promotional Sale Orders.")
            else:
                raise UserError("%s is a Promotional Order, You are not allowed to delete it." % self.name)
        return super(SaleOrder, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_promo', False):
                if vals.get('name', _('New')) == _('New'):
                    seq_date = None
                    if 'date_order' in vals:
                        seq_date = fields.Datetime.context_timestamp(self,
                                                                     fields.Datetime.to_datetime(vals['date_order']))
                    vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.promo',
                                                                        sequence_date=seq_date) or _('New')
        return super(SaleOrder, self).create(vals_list)
