from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    transportation_type = fields.Selection(related='version_id.transport_type', string="Transportation Type")