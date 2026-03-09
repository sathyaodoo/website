from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ReasonOfRefusal(models.TransientModel):
    _name = "reason.of.refusal"
    _description = "Reason Of Refusal"

    reason = fields.Text(string="Reason Of Refusal", required=True)

    def action_close_reason(self):
        active_id = self.env.context.get("active_id")
        adv = self.env["hr.advance.request"].browse(active_id)

        if adv:
            adv.write(
                {
                    "reason": (self.reason if self.reason else False),
                    "state": "refused",
                }
            )

        return {"type": "ir.actions.act_window_close"}
