from odoo import api, models, fields, _
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.tools import format_date
import logging


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    average_working_hours = fields.Float(
        string="Average Working Hours Per Month", store=True,
        related='company_id.average_working_hours', readonly=False
    )
    usd_rate_w_com = fields.Float(
        'USD Basic Rate', digits=(16, 2),
        help='USD Basic Rate For Contracts With Commission', store=True,
        related='company_id.usd_rate_w_com', readonly=False
    )
    lbp_rate_w_com = fields.Float(
        'LBP Basic Rate', digits=(16, 2),
        help='LBP Basic Rate For Contracts With Commission', store=True,
        related='company_id.lbp_rate_w_com', readonly=False
    )
    usd_rate_wot_com = fields.Float(
        'USD Basic Rate', digits=(16, 2),
        help='USD Basic Rate For Contract Without Commision', store=True,
        related='company_id.usd_rate_wot_com', readonly=False
    )
    lbp_rate_wot_com = fields.Float(
        'LBP Basic Rate', digits=(16, 2),
        help='LBP Basic Rate For Contract Without Commision', store=True,
        related='company_id.lbp_rate_wot_com', readonly=False
    )
