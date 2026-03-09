from odoo import api, models, fields, _


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    basic = fields.Boolean()
    overtime = fields.Boolean()
    undertime = fields.Boolean()
    bonus = fields.Boolean()
    commision = fields.Boolean()
    ios_comnission = fields.Boolean()
    company_loan = fields.Boolean()
    retail_loan = fields.Boolean()
    insurance = fields.Boolean()
    warning = fields.Boolean()
    deduction = fields.Boolean()
    transport = fields.Boolean()
    salary = fields.Boolean()
    net_salary = fields.Boolean()
    rounded_usd = fields.Boolean()
    rounded_LBP = fields.Boolean()
    rounded_full = fields.Boolean()
