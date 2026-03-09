from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    internal_transfer_journal_id = fields.Many2one('account.journal', string="Internal Transfer Journal",
                                                   domain=[('type', '=', 'general')])
    yearly_discount_journal_id = fields.Many2one('account.journal', string="Deferral Yearly Discount Journal",
                                                 domain=[('type', '=', 'purchase')])

    deferral_payable_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Deferral Payable Account",
        check_company=True,
        domain="[('active', '=', True), ('account_type', '=', 'liability_payable')]")

    deferral_receivable_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Deferral Receivable Account",
        check_company=True,
        domain="[('active', '=', True), ('account_type', '=', 'asset_receivable')]")
