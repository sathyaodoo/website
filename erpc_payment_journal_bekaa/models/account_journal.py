from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_journal_bekaa_in = fields.Boolean(string="Cash IN Bekaa Branch")
    is_journal_bekaa_out = fields.Boolean(string="Cash OUT Bekaa Branch")




