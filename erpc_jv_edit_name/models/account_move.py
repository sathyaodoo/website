import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    read_only = fields.Boolean(string="", compute='_compute_read_only')

    @api.depends_context('uid')
    def _compute_read_only(self):
        for move in self:
            if self.env.user.has_group('erpc_jv_edit_name.group_jv_edit_name'):
                move.read_only = False
            else:
                move.read_only = True
