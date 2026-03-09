from odoo import fields, models


class StockReservation(models.Model):
    _name = "stock.reservation.group"

    name = fields.Char("Name")


class Users(models.Model):
    _inherit = "res.users"

    reservation_group_id = fields.Many2one('stock.reservation.group', "Stock Reservation Group")
