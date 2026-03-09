from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    foreign_journal_id = fields.Many2one('account.journal', related='company_id.foreign_journal_id',
                                         readonly=False, string="Foreign Journal", check_company=True,
                                         domain="[('type', '=', 'general')]",
                                         help='The accounting journal where Foreign Purchase Entry will be registered')

    foreign_purchase_journal_id = fields.Many2one('account.journal', related='company_id.foreign_purchase_journal_id',
                                                  readonly=False, string="Foreign Purchase Journal", check_company=True,
                                                  domain="[('type', '=', 'purchase')]",
                                                  help='The accounting journal where Foreign Purchase Bill is registered')

    foreign_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.foreign_account_id',
        string="Foreign Account",
        readonly=False,
        check_company=True,
        domain="[('active', '=', True)]")

    foreign_purchase_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.foreign_purchase_account_id',
        string="Foreign Purchase Account",
        readonly=False,
        check_company=True,
        domain="[('active', '=', True), ('account_type', 'in', ('expense', 'expense_depreciation', 'expense_direct_cost'))]")


