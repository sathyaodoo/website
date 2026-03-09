from odoo import models, fields, api, _
from odoo.tools import float_utils, float_compare
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    include_stock_entry = fields.Boolean()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _validate_analytic_distribution(self):
        required_plan_ids = self.env['account.analytic.plan'].sudo().search([('account_ids', '!=', False)]).ids
        # if self.move_id.journal_id.name != 'Inventory Valuation':
        #     exclude_stock_plans = self.env['account.analytic.plan'].sudo().search(
        #         [('account_ids', '!=', False), ('include_stock_entry', '=', False)])
        #     required_plan_ids = exclude_stock_plans.ids
        # Adjust this to get the required plans
        _logger.info(f'\n\n\n\n**required_plan_ids**{required_plan_ids}\n\n\n\n.')
        for line in self:
            if not line.analytic_distribution:
                continue  # Skip if there's no analytic distribution
            plan_sums = {}
            for account_id, percentage in line.analytic_distribution.items():
                _logger.debug("Processing analytic account ID: %s", account_id)
                analytic_account = self.env['account.analytic.account'].sudo().search([('id', '=', account_id)],
                                                                                      limit=1)
                if not analytic_account:
                    _logger.error("Analytic account with ID %s does not exist.", account_id)
                    raise ValidationError(_("Analytic account with ID %s does not exist.") % account_id)
                plan_id = analytic_account.plan_id.id
                plan_name = analytic_account.plan_id.name  # Get the analytic plan name
                if plan_id not in plan_sums:
                    plan_sums[plan_id] = 0
                plan_sums[plan_id] += percentage
            # Ensure all required plans are checked
            for plan_id in required_plan_ids:
                total_percentage = plan_sums.get(plan_id, 0.0)  # Default to 0.0 if plan is missing
                _logger.debug("Total percentage for plan ID %s: %s", plan_id, total_percentage)
                compare_result = float_compare(total_percentage, 0.0, precision_digits=2)
                _logger.debug("float_compare result for 0% check (plan ID %s): %s", plan_id, compare_result)
                # Fetch the plan name for the error message
                plan = self.env['account.analytic.plan'].sudo().browse(plan_id)
                plan_name = plan.name if plan else _('Unknown')
                # Check if the plan was missing or its total percentage is 0%
                # if compare_result == 0:
                #     raise ValidationError(
                #         _("The distribution for plan '%s' is missing or totals to 0%%. Please correct the distribution.") % (
                #             plan_name)
                #     )
                # Check if the total percentage for any plan is not equal to 100%
                stock_valuation_plan = self.env['account.analytic.plan'].sudo().search(
                    [('name', '=', 'Stock Valuation')], limit=1)
                stock_valuation_plan_id = stock_valuation_plan.id if stock_valuation_plan else None
                # Check if the journal is NOT Inventory Valuation and has Stock Valuation plan
                # if line.move_id.journal_id.name != 'Inventory Valuation':
                    

                # Check the journal of the entry
                if line.move_id.journal_id.name == 'Inventory Valuation':
                    if plan_id == stock_valuation_plan_id:
                        _logger.info(
                            f"\n\n\n\n ****1111*****total_percentage*{total_percentage, total_percentage - 100}********")
                        delta = total_percentage - 100
                        if not 99 <= round(total_percentage) <= 100:
                            test = float_compare(total_percentage, 99.0, precision_digits=2)
                            _logger.info(f"\n\n\n\n *********total_percentage*{round(total_percentage), total_percentage, line.name, test}********")
                            raise ValidationError(
                                _("The sum of percentages for plan '%s' must be between 99%% and 100%% for Inventory Valuation journal entries. "
                                  "Please correct the distribution, it is '%s' in line of label '%s'.") % (plan_name, total_percentage, line.name)
                            )
                    # Get the plan record before checking include_stock_entry
                    plan = self.env['account.analytic.plan'].sudo().browse(plan_id)
                    if plan.include_stock_entry == True:
                        if plan_id != stock_valuation_plan_id and not float_compare(total_percentage, 100.0, precision_digits=2) == 0:
                            raise ValidationError(
                                _("The sum of percentages for plan '%s' is not equal to 100%%. Please correct the distribution.") % (
                                    plan_name)
                            )
                    else:
                        if float_compare(total_percentage, 0.0, precision_digits=2) > 0:
                            raise ValidationError(
                                _("stock plans can only be used with Inventory Valuation journal entries.")
                            )



                else:
                    # General constraints for other journals or plans
                    _logger.info(f"\n\n\n\n *********unreconcile test*{round(total_percentage), total_percentage, line.name, line.move_id, line.ref, line.move_id.ref, line.account_id, line.journal_id}********")
                    if plan_id == stock_valuation_plan_id and float_compare(total_percentage, 0.0, precision_digits=2) > 0:
                        raise ValidationError(
                            _("Stock Valuation plan can only be used with Inventory Valuation journal entries.")
                        )
                    if plan_id != stock_valuation_plan_id and not float_compare(total_percentage, 100.0, precision_digits=2) == 0:
                        raise ValidationError(
                            _("The sum of percentages for plan '%s' is not equal to 100%%. Please correct the distribution.") % (
                                plan_name)
                        )


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.onchange('code')
    def _onchange_code(self):
        if not self.env.user.has_group('erpc_multi_edits.group_can_edit_COA'):
            raise ValidationError(_("You cannot create a new account!"))

    def write(self, values):
        if not self.env.user.has_group('erpc_multi_edits.group_can_edit_COA'):
            raise ValidationError(_("You cannot edit an account!"))
        # Call the parent method to perform the default write operation
        return super(AccountAccount, self).write(values)

    def unlink(self):
        if not self.env.user.has_group('erpc_multi_edits.group_can_edit_COA'):
            raise ValidationError(_("You cannot delete an account!"))
        # Call the parent method to perform the default unlink operation
        return super(AccountAccount, self).unlink()


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _validate_analytic_distributions(self):
        for line in self.line_ids:
            distribution = line.analytic_distribution
            account_code = line.account_id.code
            if distribution and any(',' in key for key in distribution.keys()):
                raise ValidationError(
                    _("Analytic Distribution cannot contain multiple analytic accounts in the same line."))
            if account_code.startswith(('6', '7')):
                if not distribution:
                    raise ValidationError(_("Analytic Distribution must be set for accounts starting with 6 or 7."))
            else:
                if distribution:
                    raise ValidationError(
                        _("Analytic Distribution must not be set for accounts starting with 1, 2, 3, 4, 5"))
            line._validate_analytic_distribution()

    def action_post(self):
        self._validate_analytic_distributions()
        return super(AccountMove, self).action_post()


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    restrict_buttons = fields.Boolean(string='Restrict Buttons', compute='_compute_restrict_buttons')

    def _compute_restrict_buttons(self):
        for order in self:
            order.restrict_buttons = self.env.user.has_group('erpc_multi_edits.group_custom_sale_order_restrictions')
