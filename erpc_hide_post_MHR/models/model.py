from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    hide_mhr_post_btn = fields.Boolean(string="Hide Post", compute='_compute_hide_post_btn', store=True)

    @api.depends('company_id')
    def _compute_hide_post_btn(self):
        for move in self:
            move.hide_mhr_post_btn = move.company_id.id == 11
