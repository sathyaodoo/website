from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_custom_feature = fields.Boolean(string="Predict vendor bill account")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_custom_feature = fields.Boolean(
        string="Predict vendor bill account",
        related="company_id.enable_custom_feature",
        readonly=False
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _predict_account(self):
        _logger.info(f"hello _predict_account")
        # Check if the custom feature is enabled at the company level
        if not self.move_id.company_id.enable_custom_feature:
            return False

        # Call the parent method if the feature is enabled
        return super()._predict_account()