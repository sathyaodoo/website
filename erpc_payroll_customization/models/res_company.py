from odoo import api, models, fields, _
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.tools import format_date
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    bmr_currency = fields.Many2one('res.currency', "BMR Currency ")
    official_currency = fields.Many2one('res.currency', "Official Currency")
    average_working_hours = fields.Float("Average Working Hours Per Month")
    usd_rate_w_com = fields.Float(
        'USD Basic Rate', digits=(16, 2),
        help='USD Basic Rate For Contracts With Commission'
    )
    lbp_rate_w_com = fields.Float(
        'LBP Basic Rate', digits=(16, 2),
        help='LBP Basic Rate For Contracts With Commission'
    )
    usd_rate_wot_com = fields.Float(
        'USD Basic Rate', digits=(16, 2),
        help='USD Basic Rate For Contract Without Commission'
    )
    lbp_rate_wot_com = fields.Float(
        'LBP Basic Rate', digits=(16, 2),
        help='LBP Basic Rate For Contract Without Commission'
    )
