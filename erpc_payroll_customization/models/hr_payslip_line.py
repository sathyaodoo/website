from odoo import api, models, fields, _
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.tools import format_date
import logging


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    bmr_currency = fields.Many2one('res.currency', string="BMR Currency", related='slip_id.bmr_currency', store=True)
    bmr_currency_rate = fields.Float(string="BMR Currency Rate", compute='_compute_bmr_currency_rate', store=True, readonly=False)
    official_currency = fields.Many2one('res.currency', string="Offical Currency", related='slip_id.official_currency', store=True)
    official_currency_rate = fields.Float(string="Offical Currency Rate", related='slip_id.official_currency_rate', store=True)
    bmr_total = fields.Monetary(string='BMR Total', help='BMR Total', store=True, compute='_compute_bmr_total')
    official_total = fields.Monetary(string='Official Total', help='Official Total', store=True, compute='_compute_official_total')

    basic = fields.Boolean(string="Basic Salary", related='salary_rule_id.basic', store=True)
    overtime = fields.Boolean(string="Overtime", related='salary_rule_id.overtime', store=True)
    undertime = fields.Boolean(string="Undertime", related='salary_rule_id.undertime', store=True)
    bonus = fields.Boolean(string="Bonus", related='salary_rule_id.bonus', store=True)
    commision = fields.Boolean(string="Commission", related='salary_rule_id.commision', store=True)
    ios_comnission = fields.Boolean(string="IOS Commission", related='salary_rule_id.ios_comnission', store=True)
    company_loan = fields.Boolean(string="Company Loan", related='salary_rule_id.company_loan', store=True)
    retail_loan = fields.Boolean(string="Retail Loan", related='salary_rule_id.retail_loan', store=True)
    insurance = fields.Boolean(string="Inssurance", related='salary_rule_id.insurance', store=True)
    warning = fields.Boolean(string="Warning", related='salary_rule_id.warning', store=True)
    deduction = fields.Boolean(string="Deduction", related='salary_rule_id.deduction', store=True)
    transport = fields.Boolean(string="Transportation", related='salary_rule_id.transport', store=True)
    salary = fields.Boolean(string="Salary", related='salary_rule_id.salary', store=True)
    net_salary = fields.Boolean(string="Set Salary", related='salary_rule_id.net_salary', store=True)
    rounded_usd = fields.Boolean(string="Rounded USD", related='salary_rule_id.rounded_usd', store=True)
    rounded_LBP = fields.Boolean(string="Rounded LBP", related='salary_rule_id.rounded_LBP', store=True)
    rounded_full = fields.Boolean(string="Full Rounded Salary", related='salary_rule_id.rounded_full', store=True)
    currency_id = fields.Many2one(readonly=False, store=True)

    @api.depends('bmr_currency', 'slip_id')
    def _compute_bmr_currency_rate(self):
        for line in self:
            if line.total:
                line.bmr_currency_rate = line.slip_id.bmr_currency_rate
            else:
                line.bmr_currency_rate = 0

    @api.depends('bmr_currency', 'bmr_currency_rate', 'total', 'slip_id.bmr_currency_rate')
    def _compute_bmr_total(self):
        for line in self:
            if line.total:
                line.bmr_total = line.total * line.bmr_currency_rate
            else:
                line.bmr_total

    @api.depends('official_currency', 'official_currency_rate', 'total', 'slip_id.official_currency_rate')
    def _compute_official_total(self):
        for line in self:
            if line.total:
                line.official_total = line.total * line.official_currency_rate
            else:
                line.official_total
