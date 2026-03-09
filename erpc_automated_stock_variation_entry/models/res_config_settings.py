from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    erpc_last_inventory_value = fields.Float(string="Last Inventory Value",
                                             related='company_id.erpc_last_inventory_value',
                                             readonly=False,)

    # erpc_stock_journal_id = fields.Many2one(
    #     comodel_name='account.journal',
    #     related='company_id.erpc_stock_journal_id',
    #     readonly=False,
    #     string="Stock Inventory Journal",
    #     check_company=True,
    #     domain="[('type', '=', 'general')]")
    #
    # erpc_stock_variation_account_id = fields.Many2one(
    #     comodel_name='account.account',
    #     related='company_id.erpc_stock_variation_account_id',
    #     readonly=False,
    #     string="Stock Variation Account",
    #     check_company=True,
    #     domain="[('active', '=', True)]")
    #
    # erpc_stock_value_account_id = fields.Many2one(
    #     comodel_name='account.account',
    #     related='company_id.erpc_stock_value_account_id',
    #     readonly=False,
    #     string="Stock Value Account",
    #     check_company=True,
    #     domain="[('active', '=', True)]")
