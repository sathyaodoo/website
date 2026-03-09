from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_bekaa_branch = fields.Boolean(
        string="Bekaa Branch",
        check_company=True,
        related="company_id.is_bekaa_branch",
        readonly=False
    )
