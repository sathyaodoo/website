from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_bekaa_branch = fields.Boolean(string="Bekaa Branch")




