from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger()

class AssetsLocations(models.Model):
    _name = 'discount.form'
    _description = 'Discount Forms'

    disc = fields.Float(string="Discount")
    disc_form = fields.Char(string="Discount Form")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    disc = fields.Char(string="Discount", readonly=True, compute="_compute_disc")

    @api.depends('discount')
    def _compute_disc(self):
        for line in self:
            discount_form = self.env['discount.form'].search([('disc', '=', line.discount)], limit=1)
            if discount_form:
                line.disc = discount_form.disc_form
            else:
                line.disc = line.discount