from odoo import models, fields, api, tools, Command, _
from collections import defaultdict
from odoo.tools import formatLang
from odoo.tools.misc import frozendict
from odoo.tools import float_is_zero
import logging

_log = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_discount = fields.Boolean(string="Is Discount Line")


class LoyaltyRule(models.Model):
    _name = "loyalty.rule"
    _inherit = "loyalty.rule"

    weight = fields.Float(string="Minimum Weight", help="Minimum weight required for this rule to apply.")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'product_id')
    def _compute_totals(self):
        super()._compute_totals()  # Compute standard totals (will be zero for quantity 0)

        for line in self:
            if line.product_id.is_discount:
                # Override subtotal to unit price (ignoring quantity 0)
                line.price_subtotal = line.price_unit

                # Compute tax amount using simple percentage (as per removed field)
                tax_amount = 0.0
                if line.tax_ids:
                    for tax in line.tax_ids:
                        tax_amount += line.price_subtotal * (tax.amount / 100)

                # Set total including tax
                line.price_total = line.price_subtotal + tax_amount

    def _convert_to_tax_base_line_dict(self, **kwargs):
        """
        Convert the current record to a dictionary, ensuring that products with a family discount
        and a quantity of 0 are treated as having a quantity of 1.
        """
        self.ensure_one()

        # Get the original tax base line dictionary from the parent method
        tax_base_line_dict = super()._convert_to_tax_base_line_dict(**kwargs)
        for line in self:
            # Check if the product has a family discount (adjust field as needed)
            has_family_discount = line.product_id.is_discount
            _log.info(f"\n\n\n\n\n\n has_family_discount{has_family_discount}")

            # Override quantity if the product has a family discount and the quantity is 0
            if has_family_discount and tax_base_line_dict.get('quantity', 0) == 0:
                tax_base_line_dict['quantity'] = 1

            return tax_base_line_dict

        # Call the original method without the quantity argument
        return super(AccountMoveLine, self)._convert_to_tax_base_line_dict()

    @api.depends('tax_ids', 'currency_id', 'partner_id', 'analytic_distribution', 'balance', 'partner_id',
                 'move_id.partner_id', 'price_unit', 'quantity')
    def _compute_all_tax(self):
        for line in self:
            sign = line.move_id.direction_sign
            if line.display_type == 'tax':
                line.compute_all_tax = {}
                line.compute_all_tax_dirty = False
                continue
            if line.display_type == 'product' and line.move_id.is_invoice(True):
                amount_currency = sign * line.price_unit * (1 - line.discount / 100)
                handle_price_include = True
                if line.move_id.move_type == 'out_refund' and line.quantity == 0 and line.price_unit != 0:
                    quantity = 1
                else:
                    quantity = line.quantity
            else:
                amount_currency = line.amount_currency
                handle_price_include = False
                quantity = 1
            compute_all_currency = line.tax_ids.compute_all(
                amount_currency,
                currency=line.currency_id,
                quantity=quantity,
                product=line.product_id,
                partner=line.move_id.partner_id or line.partner_id,
                is_refund=line.is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=line.move_id.always_tax_exigible,
                fixed_multiplicator=sign,
            )
            rate = line.amount_currency / line.balance if line.balance else 1
            line.compute_all_tax_dirty = True
            line.compute_all_tax = {
                frozendict({
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'group_tax_id': tax['group'] and tax['group'].id or False,
                    'account_id': tax['account_id'] or line.account_id.id,
                    'currency_id': line.currency_id.id,
                    'analytic_distribution': (tax['analytic'] or not tax[
                        'use_in_tax_closing']) and line.analytic_distribution,
                    'tax_ids': [(6, 0, tax['tax_ids'])],
                    'tax_tag_ids': [(6, 0, tax['tag_ids'])],
                    'partner_id': line.move_id.partner_id.id or line.partner_id.id,
                    'move_id': line.move_id.id,
                    'display_type': line.display_type,
                }): {
                    'name': tax['name'] + (' ' + _('(Discount)') if line.display_type == 'epd' else ''),
                    'balance': tax['amount'] / rate,
                    'amount_currency': tax['amount'],
                    'tax_base_amount': tax['base'] / rate * (-1 if line.tax_tag_invert else 1),
                }
                for tax in compute_all_currency['taxes']
                if tax['amount']
            }
            if not line.tax_repartition_line_id:
                line.compute_all_tax[frozendict({'id': line.id})] = {
                    'tax_tag_ids': [(6, 0, compute_all_currency['base_tags'])],
                }


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        if self.move_type == 'out_refund':
            for line in self.line_ids:
                if line.quantity == 0 and line.price_unit != 0:
                    line.update({
                        'price_subtotal': line.price_unit
                    })
        # self._compute_tax_totals()
        res = super(AccountMove, self).action_post()

        return res

    def _compute_tax_totals(self):
        """ Computed field used for custom widget's rendering.
            Only set on invoices.
        """

        res = super()._compute_tax_totals()

        for move in self:
            if move.is_invoice(include_receipts=True):
                base_lines = move.invoice_line_ids.filtered(lambda line: line.display_type == 'product')
                base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]
                sign = move.direction_sign
                if move.id:
                    # The invoice is stored so we can add the early payment discount lines directly to reduce the
                    # tax amount without touching the untaxed amount.
                    base_line_values_list += [
                        {
                            **line._convert_to_tax_base_line_dict(),
                            'handle_price_include': False,
                            'quantity': 1.0,
                            'price_unit': sign * line.amount_currency,
                        }
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
                    ]

                kwargs = {
                    'base_lines': base_line_values_list,
                    'currency': move.currency_id or move.journal_id.currency_id or move.company_id.currency_id,
                }

                if move.id:
                    kwargs['tax_lines'] = [
                        line._convert_to_tax_line_dict()
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
                    ]
                else:
                    # In case the invoice isn't yet stored, the early payment discount lines are not there. Then,
                    # we need to simulate them.
                    epd_aggregated_values = {}
                    for base_line in base_lines:
                        if not base_line.epd_needed:
                            continue
                        for grouping_dict, values in base_line.epd_needed.items():
                            epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
                            epd_values['price_subtotal'] += values['price_subtotal']

                    for grouping_dict, values in epd_aggregated_values.items():
                        taxes = None
                        if grouping_dict.get('tax_ids'):
                            taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

                        kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
                            None,
                            partner=move.partner_id,
                            currency=move.currency_id,
                            taxes=taxes,
                            price_unit=values['price_subtotal'],
                            quantity=1.0,
                            account=self.env['account.account'].browse(grouping_dict['account_id']),
                            analytic_distribution=values.get('analytic_distribution'),
                            price_subtotal=values['price_subtotal'],
                            is_refund=move.move_type in ('out_refund', 'in_refund'),
                            handle_price_include=False,
                        ))
                if move.move_type == 'out_refund':
                    kwargs['is_credit_note'] = True
                move.tax_totals = self.env['account.tax']._prepare_tax_totals(**kwargs)
                if move.invoice_cash_rounding_id:
                    rounding_amount = move.invoice_cash_rounding_id.compute_difference(move.currency_id,
                                                                                       move.tax_totals['amount_total'])
                    totals = move.tax_totals
                    totals['display_rounding'] = True
                    if rounding_amount:
                        if move.invoice_cash_rounding_id.strategy == 'add_invoice_line':
                            totals['rounding_amount'] = rounding_amount
                            totals['formatted_rounding_amount'] = formatLang(self.env, totals['rounding_amount'],
                                                                             currency_obj=move.currency_id)
                            totals['amount_total_rounded'] = totals['amount_total'] + rounding_amount
                            totals['formatted_amount_total_rounded'] = formatLang(self.env,
                                                                                  totals['amount_total_rounded'],
                                                                                  currency_obj=move.currency_id)
                        elif move.invoice_cash_rounding_id.strategy == 'biggest_tax':
                            if totals['subtotals_order']:
                                max_tax_group = max((
                                    tax_group
                                    for tax_groups in totals['groups_by_subtotal'].values()
                                    for tax_group in tax_groups
                                ), key=lambda tax_group: tax_group['tax_group_amount'])
                                max_tax_group['tax_group_amount'] += rounding_amount
                                max_tax_group['formatted_tax_group_amount'] = formatLang(self.env, max_tax_group[
                                    'tax_group_amount'], currency_obj=move.currency_id)
                                totals['amount_total'] += rounding_amount
                                totals['formatted_amount_total'] = formatLang(self.env, totals['amount_total'],
                                                                              currency_obj=move.currency_id)

            else:
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals = None

        return res


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None, is_credit_note=False,
                            is_company_currency_requested=False):

        to_process = []
        for base_line in base_lines:
            if base_line.get('quantity') == 0 and is_credit_note == True:
                base_line['quantity'] = 1
            to_update_vals, tax_values_list = self._compute_taxes_for_single_line(base_line)
            to_process.append((base_line, to_update_vals, tax_values_list))

        def grouping_key_generator(base_line, tax_values):
            source_tax = tax_values['tax_repartition_line'].tax_id
            return {'tax_group': source_tax.tax_group_id}

        global_tax_details = self._aggregate_taxes(to_process, grouping_key_generator=grouping_key_generator)

        tax_group_vals_list = []
        for tax_detail in global_tax_details['tax_details'].values():
            tax_group_vals = {
                'tax_group': tax_detail['tax_group'],
                'base_amount': tax_detail['base_amount_currency'],
                'tax_amount': tax_detail['tax_amount_currency'],
            }
            if is_company_currency_requested:
                tax_group_vals['base_amount_company_currency'] = tax_detail['base_amount']
                tax_group_vals['tax_amount_company_currency'] = tax_detail['tax_amount']

            # Handle a manual edition of tax lines.
            if tax_lines is not None:
                matched_tax_lines = [
                    x
                    for x in tax_lines
                    if x['tax_repartition_line'].tax_id.tax_group_id == tax_detail['tax_group']
                ]
                if matched_tax_lines:
                    tax_group_vals['tax_amount'] = sum(x['tax_amount'] for x in matched_tax_lines)

            tax_group_vals_list.append(tax_group_vals)

        tax_group_vals_list = sorted(tax_group_vals_list,
                                     key=lambda x: (x['tax_group'].sequence, x['tax_group'].id))

        # ==== Partition the tax group values by subtotals ====

        amount_untaxed = global_tax_details['base_amount_currency']
        amount_tax = 0.0

        amount_untaxed_company_currency = global_tax_details['base_amount']
        amount_tax_company_currency = 0.0

        subtotal_order = {}
        groups_by_subtotal = defaultdict(list)
        for tax_group_vals in tax_group_vals_list:
            tax_group = tax_group_vals['tax_group']

            subtotal_title = tax_group.preceding_subtotal or _("Untaxed Amount")
            sequence = tax_group.sequence

            subtotal_order[subtotal_title] = min(subtotal_order.get(subtotal_title, float('inf')), sequence)
            groups_by_subtotal[subtotal_title].append({
                'group_key': tax_group.id,
                'tax_group_id': tax_group.id,
                'tax_group_name': tax_group.name,
                'tax_group_amount': tax_group_vals['tax_amount'],
                'tax_group_base_amount': tax_group_vals['base_amount'],
                'formatted_tax_group_amount': formatLang(self.env, tax_group_vals['tax_amount'],
                                                         currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(self.env, tax_group_vals['base_amount'],
                                                              currency_obj=currency),
            })
            if is_company_currency_requested:
                groups_by_subtotal[subtotal_title][-1]['tax_group_amount_company_currency'] = tax_group_vals[
                    'tax_amount_company_currency']
                groups_by_subtotal[subtotal_title][-1]['tax_group_base_amount_company_currency'] = tax_group_vals[
                    'base_amount_company_currency']

        # ==== Build the final result ====

        subtotals = []
        for subtotal_title in sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]):
            amount_total = amount_untaxed + amount_tax
            subtotals.append({
                'name': subtotal_title,
                'amount': amount_total,
                'formatted_amount': formatLang(self.env, amount_total, currency_obj=currency),
            })
            if is_company_currency_requested:
                subtotals[-1][
                    'amount_company_currency'] = amount_untaxed_company_currency + amount_tax_company_currency
                amount_tax_company_currency += sum(
                    x['tax_group_amount_company_currency'] for x in groups_by_subtotal[subtotal_title])

            amount_tax += sum(x['tax_group_amount'] for x in groups_by_subtotal[subtotal_title])

        amount_total = amount_untaxed + amount_tax

        display_tax_base = (len(global_tax_details['tax_details']) == 1 and currency.compare_amounts(
            tax_group_vals_list[0]['base_amount'], amount_untaxed) != 0) \
                           or len(global_tax_details['tax_details']) > 1

        return {
            'amount_untaxed': currency.round(amount_untaxed) if currency else amount_untaxed,
            'amount_total': currency.round(amount_total) if currency else amount_total,
            'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals,
            'subtotals_order': sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]),
            'display_tax_base': display_tax_base
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line, ensuring products with a family discount
        have their price_subtotal set to the unit price.
        """
        super()._compute_amount()  # Call the original computation first

        for line in self:
            # Check if the product has a family discount
            has_family_discount = line.product_id.is_discount

            if has_family_discount:
                # Override price_subtotal for discounted family products
                line.price_subtotal = line.price_unit
                tax_line_amount_e = 0

                _log.info(f"line.tax_ids: {line.tax_ids}")

                if line.tax_ids:
                    for tax_id in line.tax_ids:
                        _log.info(f"line.price_subtotal: {line.price_subtotal}")
                        tax_line_amount_e += line.price_subtotal * (tax_id.amount / 100)
                        _log.info(f"tax_line_amount_e: {tax_line_amount_e}")

                # Correct total calculation
                line.price_tax = tax_line_amount_e
                line.price_total = line.price_subtotal + tax_line_amount_e

    def _convert_to_tax_base_line_dict(self, **kwargs):
        """
        Convert the current record to a dictionary, ensuring that products with a family discount
        and a quantity of 0 are treated as having a quantity of 1.
        """
        self.ensure_one()

        # Get the original tax base line dictionary from the parent method
        tax_base_line_dict = super()._convert_to_tax_base_line_dict(**kwargs)
        for line in self:
            # Check if the product has a family discount (adjust field as needed)
            has_family_discount = line.product_id.is_discount
            _log.info(f"\n\n\n\n\n\n has_family_discount{has_family_discount}")

            # Override quantity if the product has a family discount and the quantity is 0
            if has_family_discount and tax_base_line_dict.get('quantity', 0) == 0:
                tax_base_line_dict['quantity'] = 1

            return tax_base_line_dict

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reward_id'):
                reward = self.env['loyalty.reward'].browse(vals['reward_id'])
                if reward.reward_type == 'discount':
                    vals['product_uom_qty'] = 0
        return super(SaleOrderLine, self).create(vals_list)

    def write(self, vals):
        for line in self:
            if 'reward_id' in vals or line.reward_id:
                reward = line.reward_id or self.env['loyalty.reward'].browse(vals.get('reward_id'))
                if reward and reward.reward_type == 'discount':
                    vals['product_uom_qty'] = 0  # Set quantity to 0
        return super(SaleOrderLine, self).write(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _program_check_compute_points(self, programs):
        """
        Checks the program validity from the order lines as well as computing the number of points to add.

        Returns a dict containing the error message or the points that will be given with the keys 'points'.
        """
        self.ensure_one()

        # Prepare quantities
        order_lines = self._get_not_rewarded_order_lines()
        products = order_lines.product_id
        products_qties = dict.fromkeys(products, 0)
        products_weights = dict.fromkeys(products, 0)  # Store product weights

        for line in order_lines:
            products_qties[line.product_id] += line.product_uom_qty
            products_weights[line.product_id] += line.product_id.weight * line.product_uom_qty  # Compute total weight
        # Contains the products that can be applied per rule
        products_per_rule = programs._get_valid_products(products)

        # Prepare amounts
        no_effect_lines = self._get_no_effect_on_threshold_lines()
        base_untaxed_amount = self.amount_untaxed - sum(line.price_subtotal for line in no_effect_lines)
        base_tax_amount = self.amount_tax - sum(line.price_tax for line in no_effect_lines)
        amounts_per_program = {p: {'untaxed': base_untaxed_amount, 'tax': base_tax_amount} for p in programs}

        for line in self.order_line:
            if not line.reward_id or line.reward_id.reward_type != 'discount':
                continue
            for program in programs:
                if line.reward_id.program_id.trigger == 'auto' or line.reward_id.program_id == program:
                    amounts_per_program[program]['untaxed'] -= line.price_subtotal
                    amounts_per_program[program]['tax'] -= line.price_tax

        result = {}
        for program in programs:
            untaxed_amount = amounts_per_program[program]['untaxed']
            tax_amount = amounts_per_program[program]['tax']

            code_matched = not bool(program.rule_ids) and program.applies_on == 'current'
            minimum_amount_matched = code_matched
            product_qty_matched = code_matched
            product_weight_matched = code_matched  # New weight condition

            points = 0
            rule_points = []
            program_result = result.setdefault(program, dict())

            for rule in program.rule_ids:
                if rule.mode == 'with_code' and rule not in self.code_enabled_rule_ids:
                    continue
                code_matched = True
                rule_amount = rule._compute_amount(self.currency_id)
                if rule_amount > (
                        rule.minimum_amount_tax_mode == 'incl' and (untaxed_amount + tax_amount) or untaxed_amount):
                    continue
                minimum_amount_matched = True

                if not products_per_rule.get(rule):
                    continue

                rule_products = products_per_rule[rule]
                ordered_rule_products_qty = sum(products_qties[product] for product in rule_products)
                ordered_rule_products_weight = sum(
                    products_weights[product] for product in rule_products)  # Compute total weight for rule

                if (
                        ordered_rule_products_qty < rule.minimum_qty or ordered_rule_products_weight < rule.weight) or not rule_products:
                    continue
                product_qty_matched = True
                product_weight_matched = True

                if not rule.reward_point_amount:
                    continue

                if program.applies_on == 'future' and rule.reward_point_split and rule.reward_point_mode != 'order':
                    if rule.reward_point_mode == 'unit':
                        rule_points.extend(rule.reward_point_amount for _ in range(int(ordered_rule_products_qty)))
                    elif rule.reward_point_mode == 'money':
                        for line in self.order_line:
                            if line.is_reward_line or line.product_id not in rule_products or line.product_uom_qty <= 0:
                                continue
                            points_per_unit = float_round(
                                (rule.reward_point_amount * line.price_total / line.product_uom_qty),
                                precision_digits=2, rounding_method='DOWN')
                            if not points_per_unit:
                                continue
                            rule_points.extend([points_per_unit] * int(line.product_uom_qty))
                else:
                    if rule.reward_point_mode == 'order':
                        points += rule.reward_point_amount
                    elif rule.reward_point_mode == 'money':
                        amount_paid = sum(
                            max(0, line.price_total) for line in order_lines if line.product_id in rule_products)
                        points += float_round(rule.reward_point_amount * amount_paid, precision_digits=2,
                                              rounding_method='DOWN')
                    elif rule.reward_point_mode == 'unit':
                        points += rule.reward_point_amount * ordered_rule_products_qty

            if not program.is_nominative:
                if not code_matched:
                    program_result['error'] = _("This program requires a code to be applied.")
                elif not minimum_amount_matched:
                    program_result['error'] = _(
                        'A minimum of %(amount)s %(currency)s should be purchased to get the reward',
                        amount=min(program.rule_ids.mapped('minimum_amount')),
                        currency=program.currency_id.name,
                    )
                elif not product_qty_matched:
                    program_result['error'] = _("You don't have the required product quantities on your sales order.")
                elif not product_weight_matched:  # New error message for weight condition
                    program_result['error'] = _("You don't have the required product weight on your sales order.")
            elif not self._allow_nominative_programs():
                program_result['error'] = _("This program is not available for public users.")
            if 'error' not in program_result:
                points_result = [points] + rule_points
                program_result['points'] = points_result

        return result

    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`, including lines from the 'Discount' family even if qty is 0."""
        # Call the original method to get the default invoiceable lines
        invoiceable_lines = super(SaleOrder, self)._get_invoiceable_lines(final=final)

        # Define the product family you want to include

        # Create a set to hold the IDs of the invoiceable lines
        invoiceable_line_ids = set(invoiceable_lines.ids)

        for line in self.order_line:
            # Check if the line is from the discount family
            has_family_discount = line.product_id.is_discount
            # Include lines from the discount family even if qty_to_invoice is 0
            if has_family_discount and line.id not in invoiceable_line_ids:
                invoiceable_line_ids.add(line.id)

        # Return the updated invoiceable lines
        return self.env['sale.order.line'].browse(list(invoiceable_line_ids))


class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    def _get_discount_product_values(self):
        product_values = super()._get_discount_product_values()
        for values in product_values:
            values['is_discount'] = True  # set the boolean flag
        return product_values

    def write(self, values):
        # Check if 'active' is being set to False
        if 'active' in values and not values['active']:
            # If the 'discount_line_product_id' is set, unlink the related product
            for reward in self:
                if reward.discount_line_product_id:
                    product_id = reward.discount_line_product_id.id
                    _log.info(f"\\n\n\n\n\n\n\n {product_id} product_id \n\n\n\n\n\n\n ")
                    reward.discount_line_product_id = False  # Store the product ID
                    # Search for the product by its ID and unlink it
                    _log.info(f"\\n\n\n\n\n\n\n {product_id} product_id 22 \n\n\n\n\n\n\n ")

                    product = self.env['product.product'].browse(product_id)
                    _log.info(f"\\n\n\n\n\n\n\n {product_id} product_id 23 \n\n\n\n\n\n\n ")

                    product.write({'active': False})
                    product.product_tmpl_id.write({'active': False})  # Unlink (delete) the product
                    # Then set the discount_line_product_id to False

        # Call the parent class's write function to ensure the original functionality
        return super(LoyaltyReward, self).write(values)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        invoice = super()._create_invoices(sale_orders)  # Call the original function
        _log.info(f"\n\n\n\n\n\n\n innnnnnnnnnnn")

        for order in sale_orders:
            # Find ALL sale order lines where product's family_is == 'Discount'
            discount_lines = order.order_line.filtered(lambda l: l.product_id.is_discount)
            _log.info(f"\n\n\n\n\n\n\n discount_lines: {discount_lines}")

            discount_tax_amount = 0
            for discount_line in discount_lines:
                if discount_line.tax_id:
                    for tax in discount_line.tax_id:
                        discount_tax_amount += discount_line.price_subtotal * (tax.amount / 100)

            _log.info(f"\n\n\n\n\n\n\n discount_tax_amount: {discount_tax_amount}")

            if discount_tax_amount:
                # Find the tax line in the invoice with account "442700 VAT COLLECTED ON SALES"
                tax_line = invoice.line_ids.filtered(lambda l: l.account_id.code == '442700')[:1]

                if tax_line:
                    # Subtract the computed tax amount from the specific tax line
                    tax_line.amount_currency -= discount_tax_amount

        return invoice
