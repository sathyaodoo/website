from odoo import models, fields, api, _



class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_receivable_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.company_receivable_account_id',
        string="Company Receivable Account",
        readonly=False,
        check_company=True,
        domain="[('active', '=', True), ('account_type', '=', 'asset_receivable')]")

    company_payable_account_id = fields.Many2one(
        comodel_name='account.account',
        related='company_id.company_payable_account_id',
        string="Company Payable Account",
        readonly=False,
        check_company=True,
        domain="[('active', '=', True), ('account_type', '=', 'liability_payable')]")