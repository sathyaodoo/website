from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    foreign_journal_id = fields.Many2one('account.journal', string="Foreign Journal",
                                                  domain=[('type', '=', 'general')])
    foreign_purchase_journal_id = fields.Many2one('account.journal', string="Foreign Purchase Journal",
                                                  domain=[('type', '=', 'purchase')])

    foreign_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Foreign Account",
        check_company=True,
        domain="[('active', '=', True)]")

    foreign_purchase_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Foreign Purchase Account",
        check_company=True,
        domain="[('active', '=', True), ('account_type', 'in', ('expense', 'expense_depreciation', 'expense_direct_cost'))]")


