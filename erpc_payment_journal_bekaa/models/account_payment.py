from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('payment_type', 'company_id')
    def _onchange_payment_type_branch_default_journal(self):
        if self.company_id.is_bekaa_branch:
            if self.payment_type == 'inbound':
                in_bekaa_journal = self.env['account.journal'].sudo().search(
                    [('is_journal_bekaa_in', '=', True)], limit=1)
                if not in_bekaa_journal:
                    raise UserError(_("Please configure the 'In Journal' in the journals of 'Bekaa Branch'."))

                journal = in_bekaa_journal
            elif self.payment_type == 'outbound':
                out_bekaa_journal = self.env['account.journal'].sudo().search(
                    [('is_journal_bekaa_out', '=', True)], limit=1)
                if not out_bekaa_journal:
                    raise UserError(_("Please configure the 'Out Journal' in the journals of 'Bekaa Branch'."))
                journal = out_bekaa_journal
            self.journal_id = journal
