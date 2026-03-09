from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    request_item_count = fields.Integer(string="Request Item Count", compute='_compute_request_item_count')

    def _compute_request_item_count(self):
        for rec in self:
            rec.request_item_count = self.env['request.item'].search_count([
                ('employee_id', '=', rec.id)
            ])
