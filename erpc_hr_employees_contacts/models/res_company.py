from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    company_receivable_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Company Receivable Account",
        check_company=True,
        domain="[('active', '=', True), ('account_type', '=', 'asset_receivable')]")

    company_payable_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Company Payable Account",
        check_company=True,
        domain="[('active', '=', True), ('account_type', '=', 'liability_payable')]")
