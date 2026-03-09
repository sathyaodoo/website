from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)


# TODO GR: to check what to replace in odoo 19
# class AccountBudgetPost(models.Model):
#     _inherit = 'account.budget.post'

# TODO GR: to check what to replace in odoo 19
# @api.constrains('account_ids', 'financial_group_id', 'company_id')
# def _check_account_financial(self):
#     for budget in self:
#         for account in budget.account_ids:
#             if account.company_id != budget.company_id or account.financial_group_id != budget.financial_group_id:
#                 _logger.info(f'\n\n\n\n*****not same financial group****{account.financial_group_id}\n\n\n\n.')
#                 _logger.info(
#                     f'\n\n*****Account Company ID: {account.company_id.name, account.code}, Budget Company ID: {budget.company_id.name, budget.id}\n\n')
#                 raise ValidationError(
#                     _("All accounts on a Budget must belong to the same Company and Financial Group as that Budget."))


# TODO : to check what to replace in odoo 19
# def write(self, vals):
#     _logger.info(f"\n\n*****vals****{vals}\n\n.")
#     # capture pre-state per BP
#     pre_codes_map = {bp.id: set(bp.account_ids.mapped('code')) for bp in self}

#     res = super(AccountBudgetPost, self).write(vals)

#     if 'account_ids' in vals and not self.env.context.get('skip_sync'):
#         for bp in self:
#             old_codes = pre_codes_map.get(bp.id, set())
#             new_codes = set(bp.account_ids.mapped('code'))
#             added_codes = {c for c in (new_codes - old_codes) if c}
#             removed_codes = {c for c in (old_codes - new_codes) if c}

#             _logger.info(
#                 f"\n\nadded={sorted(added_codes)} removed={sorted(removed_codes)} for BP {bp.display_name}\n\n.")

#             # ---- Mirror on Chart of Account (same company) if you need it ----
#             if added_codes:
#                 acc_add_self = self.env['account.account'].sudo().search([
#                     ('company_id', '=', bp.company_id.id),
#                     ('code', 'in', list(added_codes)),
#                 ])
#                 if acc_add_self:
#                     acc_add_self.with_context(skip_sync=True).sudo().write({'general_budget_id': bp.id})

#             if removed_codes:
#                 acc_rm_self = self.env['account.account'].sudo().search([
#                     ('company_id', '=', bp.company_id.id),
#                     ('code', 'in', list(removed_codes)),
#                 ])
#                 to_clear = acc_rm_self.filtered(lambda a: a.general_budget_id.id == bp.id)
#                 if to_clear:
#                     to_clear.with_context(skip_sync=True).sudo().write({'general_budget_id': False})

#             # ---- Apply to other companies' BPs with the SAME Financial Group ----
#             related_posts = self.sudo().search([
#                 ('id', '!=', bp.id),
#                 ('financial_group_id', '=', bp.financial_group_id.id),
#             ])

#             for rp in related_posts:
#                 # ADD
#                 if added_codes:
#                     accs = self.env['account.account'].sudo().search([
#                         ('company_id', '=', rp.company_id.id),
#                         ('code', 'in', list(added_codes)),
#                     ])
#                     if accs:
#                         # ensure FG matches (if you enforce "accounts must have same FG as BP")
#                         to_fix_fg = accs.filtered(lambda a: a.financial_group_id.id != rp.financial_group_id.id)
#                         if to_fix_fg:
#                             _logger.info("Aligning FG on %s in %s to %s",
#                                          sorted(to_fix_fg.mapped('code')), rp.company_id.display_name,
#                                          rp.financial_group_id.display_name)
#                             to_fix_fg.with_context(skip_sync=True).sudo().write({
#                                 'financial_group_id': rp.financial_group_id.id
#                             })
#                         rp.with_context(skip_sync=True).sudo().write({
#                             'account_ids': [(4, acc_id) for acc_id in accs.ids]
#                         })

#                 # REMOVE
#                 if removed_codes:
#                     accs_rm = self.env['account.account'].sudo().search([
#                         ('company_id', '=', rp.company_id.id),
#                         ('code', 'in', list(removed_codes)),
#                     ])
#                     if accs_rm:
#                         rp.with_context(skip_sync=True).sudo().write({
#                             'account_ids': [(3, acc_id) for acc_id in accs_rm.ids]
#                         })

#     return res


# class AccountAccount(models.Model):
#     _inherit = 'account.account'
#
#     is_required_position = fields.Boolean(compute="_compute_is_required_position")
#
#     # TODO : to fix - FOUAAD
#     general_budget_id = fields.Many2one(
#         'account.budget.post',
#         string='Budgetary Position',
#         domain="[('company_id', '=', company_id), ('financial_group_id', '=', financial_group_id)]",
#     )
#
#     @api.depends('root_id', 'financial_group_id', 'financial_type')
#     def _compute_is_required_position(self):
#         for account in self:
#             if account.financial_type == 'pl':
#                 if account.code.startswith(('6', '7')):
#                     account.is_required_position = True
#                 else:
#                     account.is_required_position = False
#             else:
#                 account.is_required_position = False


    # TODO : to check what to replace in odoo 19
    # def _matching_budget_for_account(self):
    #     """Return the budgetary position (account.budget.post) that matches this account's company + financial group.
    #     Preference:
    #       1) use general_budget_id if it matches
    #       2) else, search one by (company_id, financial_group_id)
    #     """
    #     self.ensure_one()
    #     bud = self.general_budget_id
    #     if bud and bud.company_id == self.company_id and bud.financial_group_id == self.financial_group_id:
    #         return bud
    #     if self.company_id and self.financial_group_id:
    #         return self.env['account.budget.post'].sudo().search([
    #             ('company_id', '=', self.company_id.id),
    #             ('financial_group_id', '=', self.financial_group_id.id),
    #         ], limit=1)
    #     return self.env['account.budget.post']  # empty recordset


    # TODO : to check what to replace in odoo 19
    # def write(self, vals):
    #     # Track old links to remove when needed
    #     prev_budget_by_rec = {rec.id: rec._matching_budget_for_account().id or False for rec in self}

    #     res = super().write(vals)

    #     # Reconcile links after changes
    #     for rec in self:
    #         new_target = rec._matching_budget_for_account()
    #         new_id = new_target.id or False
    #         old_id = prev_budget_by_rec.get(rec.id)

    #         # If matching target changed, remove from old and add to new
    #         if old_id and old_id != new_id:
    #             self.env['account.budget.post'].sudo().browse(old_id).write({
    #                 'account_ids': [Command.unlink(rec.id)]
    #             })
    #         if new_id:
    #             new_target.sudo().write({'account_ids': [Command.link(rec.id)]})

    #     return res

    # TODO : to check what to replace in odoo 19
    # @api.onchange('general_budget_id')
    # def _onchange_general_budget_id_warn_cross_company(self):
    #     for rec in self:
    #         if not (rec.code and rec.general_budget_id):
    #             continue

    #         target = rec._matching_budget_for_account()
    #         if not target:
    #             continue

    #         # Same account code in other companies that don't match the new target
    #         others = self.env['account.account'].sudo().search([
    #             ('code', '=', rec.code),
    #             ('company_id', '!=', rec.company_id.id),
    #         ])
    #         if others:
    #             companies = ', '.join(others.mapped('company_id.name'))
    #             return {
    #                 'warning': {
    #                     'title': _("Cross-company reminder"),
    #                     'message': _(
    #                         "You set Budgetary Position to '%(post)s' for account code %(code)s.\n"
    #                         "Please mirror this change in other companies: %(companies)s",
    #                         post=target.display_name, code=rec.code, companies=companies
    #                     ),
    #                 }
    #             }
    #     return {}


class CrossoveredBudget(models.Model):
    _inherit = "budget.analytic"

    def action_budget_draft(self):
        if self.state == 'done' and not self.env.user.has_group('erpc_budgetary_constraints.group_approve_budgets'):
            raise AccessError(_("You don't have the access rights to reset to draft a done budget."))
        self.write({'state': 'draft'})


# class CrossoveredBudgetLines(models.Model):
#     _inherit = "crossovered.budget.lines"

#     stored_practical_amount = fields.Monetary(
#         string='Amount Practical', help="Amount really earned/spent.")

#     stored_theoritical_amount = fields.Monetary(
#         string='Amount Theoretical',
#         help="Amount you are supposed to have earned/spent at this date.")

#     # TODO : to uncomment
#     # @api.constrains('general_budget_id', 'crossovered_budget_id')
#     # def _must_have_same_budget_name(self):
#     #     for record in self:
#     #         if record.general_budget_id.name != record.crossovered_budget_id.name:
#     #             raise ValidationError(
#     #                 _("You have to enter a budgetary position having same Budget name."))

#     def _compute_practical_amount(self):
#         res = super()._compute_practical_amount()
#         for line in self:
#             line.stored_practical_amount = line.practical_amount
#         return res

#     @api.depends('date_from', 'date_to')
#     def _compute_theoritical_amount(self):
#         res = super()._compute_theoritical_amount()
#         for line in self:
#             line.stored_theoritical_amount = line.theoritical_amount
#         return res


#     # TODO : to uncomment
#     # def action_open_budget_entries(self):
#     #     if self.analytic_account_id:
#     #         # if there is an analytic account, then the analytic items are loaded
#     #         action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action_entries')
#     #         action['domain'] = [('auto_account_id', '=', self.analytic_account_id.id),
#     #                             ('date', '>=', self.date_from),
#     #                             ('date', '<=', self.date_to)
#     #                             ]
#     #         if self.general_budget_id:
#     #             action['domain'] += [('general_account_id', 'in', self.general_budget_id.account_ids.ids)]
#     #         action['context'] = {'group_by': 'general_account_id'}
#     #     else:
#     #         # otherwise the journal entries booked on the accounts of the budgetary postition are opened
#     #         action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
#     #         action['domain'] = [('account_id', 'in',
#     #                              self.general_budget_id.account_ids.ids),
#     #                             ('date', '>=', self.date_from),
#     #                             ('date', '<=', self.date_to)
#     #                             ]
#     #         action['context'] = {'group_by': 'account_id'}
#     #     return action
