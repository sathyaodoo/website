# from odoo import api, fields, models, _
# from odoo.exceptions import ValidationError
# import logging
#
# _logger = logging.getLogger(__name__)


# class AccountBudgetPost(models.Model):
#     _inherit = 'account.budget.post'
#
#     financial_group_id = fields.Many2one('account.financial.group', string='Financial Group', required=True)
#     name = fields.Char('Name', required=True, compute='_compute_budgetary_name', store=True, precompute=True)
#
#     @api.depends('financial_group_id')
#     def _compute_budgetary_name(self):
#         for budget in self:
#             if budget.financial_group_id:
#                 budget.name = budget.financial_group_id.name
#
#     @api.constrains('company_id', 'financial_group_id')
#     def check_budget_company(self):
#         for budget in self:
#             if budget.financial_group_id:
#                 existing_budgets = budget.search(
#                     [('id', '!=', budget.id or budget.id.origin), ('company_id', '=', budget.company_id.id),
#                      ('name', '=', budget.financial_group_id.name)])
#                 if existing_budgets:
#                     raise ValidationError(
#                         "The budget Name must be Unique per Company.")
#
#     @api.model
#     def create(self, vals):
#         if self.env.context.get('budget_replication'):
#             return super(AccountBudgetPost, self).create(vals)
#
#         budget = super(AccountBudgetPost, self).create(vals)
#
#         main_company_id = vals.get('company_id')
#
#         other_companies = self.env['res.company'].sudo().search([('id', '!=', main_company_id)])
#
#         for company in other_companies:
#             vals_copy = vals.copy()
#             vals_copy['company_id'] = company.id
#
#             _logger.info(
#                 f'\n\n*****Company ID: {company.id}, Financial Group ID: {vals_copy["financial_group_id"]}\n\n')
#
#             existing_budgets = self.env['account.budget.post'].sudo().search(
#                 [('company_id', '=', company.id), ('financial_group_id', '=', vals_copy['financial_group_id'])]
#             )
#
#             if existing_budgets:
#                 raise ValidationError(
#                     f"A budget with the financial group {existing_budgets.financial_group_id.name} "
#                     f"already exists for company {company.name}."
#                 )
#
#             main_company_account_codes = budget.account_ids.mapped('code')
#
#             company_specific_accounts = self.env['account.account'].search([
#                 ('code', 'in', main_company_account_codes),
#                 ('company_id', '=', company.id)
#             ])
#             if not company_specific_accounts:
#                 raise ValidationError(
#                     f'No accounts available for company {company.name} that match the main company codes.')
#
#             missing_account_codes = set(main_company_account_codes) - set(company_specific_accounts.mapped('code'))
#
#             if missing_account_codes:
#                 raise ValidationError(
#                     f'The following accounts from the main company are not found in the chart of accounts for company {company.name}: {", ".join(missing_account_codes)}. '
#                     f'The budget cannot be created without these accounts.'
#                 )
#
#             vals_copy['account_ids'] = [(6, 0, company_specific_accounts.ids)]
#
#             self.env['account.budget.post'].with_context(budget_replication=True).create(vals_copy)
#
#         return budget


# class CrossoveredBudget(models.Model):
#     _inherit = "crossovered.budget"
#     _order = "name"
