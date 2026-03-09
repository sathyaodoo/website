# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if any(order.is_promo for order in sale_orders):
            raise UserError("Promotional Sale Orders can't be Invoiced")
        return super(SaleAdvancePaymentInv, self).create_invoices()