from odoo import fields, models, api
import logging

_log = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    asset_model_id = fields.Many2one('account.asset', string='Model', related="account_id.asset_model", store=True,
                                     copy=False)
