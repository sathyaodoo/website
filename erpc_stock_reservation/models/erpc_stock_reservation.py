from odoo import models, fields, api, _
from datetime import datetime, timedelta


class StockReservation(models.Model):
    _inherit = 'stock.reservation'
    show_reserve_button = fields.Boolean(compute='_compute_show_reserve_button', default=False)

    @api.depends('date_validity')
    def _compute_show_reserve_button(self):
        for record in self:
            if record.date_validity:
                date_validity = fields.Date.from_string(record.date_validity)
                days_before_validity = date_validity - timedelta(days=5)
                record.show_reserve_button = days_before_validity <= datetime.today().date() < date_validity

            else:
                record.show_reserve_button = False


    def Reserve_again_button_action(self):
        print('Button clicked')
        for record in self:
            if record.date_validity:
                date_validity = fields.Date.from_string(record.date_validity)
                new_date_validity = date_validity + timedelta(days=30)
                record.date_validity = new_date_validity