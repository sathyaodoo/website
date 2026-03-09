from odoo import models, fields


class AccountFinancialGroup(models.Model):
    _name = 'account.financial.group'
    _description = 'Account Financial Group'

    name = fields.Char(string='Name', required=True)
    type = fields.Selection([
        ('bs', 'Balance Sheet'),
        ('pl', 'Profit & Loss')
    ], string='Type', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=False, default=lambda self: self.env.company,
                                 readonly=False)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    financial_group_id = fields.Many2one('account.financial.group', string='Financial Group')
    financial_type = fields.Selection([
        ('bs', 'Balance Sheet'),
        ('pl', 'Profit & Loss')
    ], string='Financial Type', related="financial_group_id.type")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    financial_group_id = fields.Many2one('account.financial.group', string='Financial Group',
                                         related='account_id.financial_group_id', store=True)
    financial_type = fields.Selection([
        ('bs', 'Balance Sheet'),
        ('pl', 'Profit & Loss')
    ], string='Financial Type', related="financial_group_id.type", store=True)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    financial_group_id = fields.Many2one('account.financial.group', string='Financial Group',
                                         related='general_account_id.financial_group_id', store=True)
    financial_type = fields.Selection([
        ('bs', 'Balance Sheet'),
        ('pl', 'Profit & Loss')
    ], string='Financial Type', related="financial_group_id.type", store=True)