from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    expected_arrival_date = fields.Datetime(
        string="Expected Arrival Date",
        compute="_compute_expected_arrival",
        store=True,
    )

    @api.depends("purchase_line_id", "purchase_line_id.date_planned")
    def _compute_expected_arrival(self):
        for rec in self:
            rec.expected_arrival_date = (
                rec.purchase_line_id.date_planned if rec.purchase_line_id else False
            )
