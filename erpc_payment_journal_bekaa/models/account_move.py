from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            if self.env.user.has_group('erpc_payment_journal_bekaa.group_bekaa_user'):
                if move.move_type in ['entry', 'in_invoice']:  # Misc & Vendor Bill
                    raise UserError("Bekaa users cannot post this type of entry.")
        return super().action_post()