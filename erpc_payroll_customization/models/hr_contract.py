from odoo import api, models, fields, _
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import format_date
import logging


class HRVersion(models.Model):
    _inherit = 'hr.version'

    hourly_rate = fields.Float('Hourly Rate', digits=(16, 2), compute='_compute_hourly_rate')
    bmr_currency = fields.Many2one('res.currency', string="BMR Currency ", related='company_id.bmr_currency', store=True)
    transport = fields.Monetary(string='Transportation / Day', help='Transportation amount added to the salary per day.')
    # usd_rate = fields.Float('USD Basic Rate', digits=(16, 2))
    # lbp_rate = fields.Float('LBP Basic Rate', digits=(16, 2))
    category = fields.Selection([
        ('with_commission', 'With Commission'),
        ('without_commission', 'Without Commission')
    ], default='', string='Commission Scheme', required=True)
    transport_type = fields.Selection([
        ('no_transport', 'No Transportation'),
        ('based_on_attendance', 'Based On Attendance'),
        ('bulk', 'Bulk')
    ], default='', string='Transportation Type', required=True)
    transport_bulk = fields.Monetary(string='Transportation Bulk Amount', help='Transportation bulk amount.')

    @api.depends('wage')
    def _compute_hourly_rate(self):
        for contract in self:
            if contract.wage:
                contract.hourly_rate = contract.wage / contract.company_id.average_working_hours
            else:
                contract.hourly_rate = 0

    # @api.onchange('category')
    # def _onchange_category(self):
    #     if self.category == 'with_commission':
    #         self.usd_rate = self.company_id.usd_rate_w_com
    #         self.lbp_rate = self.company_id.lbp_rate_w_com
    #     else:
    #         self.usd_rate = self.company_id.usd_rate_wot_com
    #         self.lbp_rate = self.company_id.lbp_rate_wot_com
