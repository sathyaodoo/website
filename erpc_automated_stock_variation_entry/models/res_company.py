from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    erpc_last_inventory_value = fields.Float(string="Last Inventory Value")

    # erpc_stock_journal_id = fields.Many2one(
    #     comodel_name='account.journal',
    #     string="Stock Inventory Journal",
    #     domain=[('type', '=', 'general')])
    #
    # erpc_stock_variation_account_id = fields.Many2one(
    #     comodel_name='account.account',
    #     string="Stock Variation Account",
    #     check_company=True,  # Remove company_dependent=True
    #     domain="[('active', '=', True)]")
    #
    # erpc_stock_value_account_id = fields.Many2one(
    #     comodel_name='account.account',
    #     string="Stock Value Account",
    #     check_company=True,  # Remove company_dependent=True
    #     domain="[('active', '=', True)]")