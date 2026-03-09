from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    internal_transfer_journal_id = fields.Many2one('account.journal', related='company_id.internal_transfer_journal_id',
                                                   readonly=False, string="Internal Transfer Journal",
                                                   check_company=True,
                                                   domain="[('type', '=', 'general')]",
                                                   help='The accounting journal where Yearly Discount Transfer Entry will be registered')

    yearly_discount_journal_id = fields.Many2one('account.journal', related='company_id.yearly_discount_journal_id',
                                                 readonly=False, string="Deferral Yearly Discount Journal", check_company=True,
                                                 domain="[('type', '=', 'purchase')]",
                                                 help='The accounting journal where deferral Yearly Discount Bill is registered')

    deferral_payable_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.deferral_payable_account_id',
        string="Deferral Payable Account",
        readonly=False,
        check_company=True,
        domain="[('active', '=', True), ('account_type', '=', 'liability_payable')]")

    deferral_receivable_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.deferral_receivable_account_id',
        string="Deferral Receivable Account",
        readonly=False,
        check_company=True,
        domain="[('active', '=', True), ('account_type', '=', 'asset_receivable')]")
