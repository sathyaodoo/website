from odoo import models, _, fields, api
from odoo.tools.misc import get_lang
import logging

_logger = logging.getLogger(__name__)


class CashFlowInOutReportHandler(models.AbstractModel):
    _name = 'account.cash.flow.in.out.report.handler'
    _inherit = 'account.report.custom.handler'
    _description = 'Cash Flow In/Out Report Handler'

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):
        _logger.info(f"--- _dynamic_lines_generator called ---")
        _logger.info(f"Options unfolded_lines: {options.get('unfolded_lines')}")
        lines = []
        layout_data = self._get_layout_data()
        report_data = self._get_report_data(report, options, layout_data)

        for layout_line_id, layout_line_data in layout_data.items():
            # 1) Top-level
            lines.append((0, self._get_layout_line(report, options, layout_line_id, layout_line_data, report_data)))

            # 2) Drill-down to accounts everywhere except cash_in/cash_out
            if layout_line_id not in ('cash_in', 'cash_out') and layout_line_id in report_data:
                for acc_data in sorted(
                        report_data[layout_line_id]['aml_groupby_account'].values(),
                        key=lambda x: (x.get('account_code') or x.get('account_name') or '').lower()
                ):
                    lines.append((0, self._get_account_line(report, options, acc_data)))

            # 3) Under cash_in / cash_out: category → parent-company
            if layout_line_id in ('cash_in', 'cash_out') and layout_line_id in report_data:
                for cat_data in sorted(
                        report_data[layout_line_id]['aml_groupby_account'].values(),
                        key=lambda x: (x.get('account_name') or '').lower()
                ):
                    # build & mark category rows
                    cat_line = self._get_category_line(report, options, cat_data)

                    lines.append((0, cat_line))
                    _logger.info(
                        f"Category line: {cat_line['name']} (ID: {cat_line['id']}), Unfolded: {cat_line['unfolded']}")

                    for child in sorted(
                            cat_data.get('child_lines', []),
                            key=lambda c: (c.get('parent_company_name') or '').lower()
                    ):
                        # if there's no parent_company_name, use the literal string "None"
                        company_name = child.get('parent_company_name') or 'None'
                        comp = {
                            'parent_line_id': cat_line['id'],
                            'parent_company_id': child.get('parent_company_id'),
                            'parent_company_name': company_name,
                            'balance': child['balance'],
                            'level': cat_data['level'] + 1,
                        }
                        # give the handler the list of partners so it can set unfoldable=True
                        comp['child_lines'] = child.get('child_lines', [])
                        child_line = self._get_parent_company_line(report, options, comp)
                        lines.append((0, child_line))
                        company_line_id = child_line['id']
                        for partner_child in sorted(
                                child.get('child_lines', []),
                                key=lambda c: (c.get('partner_name') or '').lower()
                        ):
                            # if there's no parent_company_name, use the literal string "None"
                            partner_name = partner_child.get('partner_name') or 'None'
                            part = {
                                'parent_line_id': company_line_id,
                                'partner_id': partner_child.get('partner_id'),
                                'partner_name': partner_name,
                                'balance': partner_child['balance'],
                                'level': child['level'] + 1,
                            }
                            # give the handler the actual payments so unfoldable=True
                            part['child_lines'] = partner_child.get('child_lines', [])
                            partner_child_line = self._get_partner_line(report, options, part)
                            lines.append((0, partner_child_line))
                            partner_line_id = partner_child_line['id']
                            for pay in partner_child.get('child_lines', []):
                                pay_part = {
                                    'parent_line_id': partner_line_id,
                                    'payment_id': pay['payment_id'],
                                    'payment_name': pay['payment_name'],
                                    'balance': pay['balance'],
                                    'level': pay['level'],
                                }
                                pay_line = self._get_payment_line(report, options, pay_part)
                                lines.append((0, pay_line))

                        _logger.debug(f"  Loaded child for DOM: {child_line['name']} under {cat_line['name']}")
        _logger.info(f"--- _dynamic_lines_generator finished, total lines: {len(lines)} ---")
        return lines

    def _custom_options_initializer(self, report, options, previous_options=None):
        super()._custom_options_initializer(report, options, previous_options=previous_options)
        report._init_options_journals(options, previous_options=previous_options,
                                      additional_journals_domain=[('type', 'in', ('bank', 'cash', 'general'))])

    def _get_report_data(self, report, options, layout_data):
        report_data = {}

        payment_account_ids = self._get_account_ids(report, options)
        if not payment_account_ids:
            return report_data
        currency_table_query = report._get_query_currency_table(options)

        # Compute 'Cash and cash equivalents, beginning of period'
        for aml_data in self._compute_liquidity_balance(report, options, currency_table_query, payment_account_ids,
                                                        'to_beginning_of_period'):
            self._add_report_data('opening_balance', aml_data, layout_data, report_data)
            self._add_report_data('closing_balance', aml_data, layout_data, report_data)

        # Compute 'Cash and cash equivalents, closing balance'
        for aml_data in self._compute_liquidity_balance(report, options, currency_table_query, payment_account_ids,
                                                        'strict_range'):
            self._add_report_data('closing_balance', aml_data, layout_data, report_data)
            _logger.info(f"\n\n\n closing_balance _add_report_data: {layout_data} \n\n\n")

        # Cash In
        cash_ins = self._compute_cash_flow(report, options, currency_table_query, payment_account_ids,
                                           flow_type='in') or []
        for cf in cash_ins:
            self._add_report_data('cash_in', cf, layout_data, report_data)

        # Cash Out
        cash_outs = self._compute_cash_flow(report, options, currency_table_query, payment_account_ids,
                                            flow_type='out') or []
        for cf in cash_outs:
            self._add_report_data('cash_out', cf, layout_data, report_data)

        return report_data

    def _add_report_data(self, layout_line_id, aml_data, layout_data, report_data):
        """
        Add one row of aml_data into report_data.

        report_data[layout_line_id] = {
            'balance': { column_group_key: total_amount, … },
            'aml_groupby_account': {
                account_id: {
                    parent_line_id, account_id, account_code, account_name,
                    level, balance: { column_group_key: amount, … },
                    # for cash_in / cash_out only:
                    child_lines: [ { parent_line_id, parent_company_id,
                                    parent_company_name, column_group_key, balance, level }, … ]
                }, …
            }
        }
        """

        def _bubble_up(line, col_key, amount):
            # recursively add to parent sections
            parent = layout_data[line].get('parent_line_id')
            if not parent:
                return
            report_data.setdefault(parent, {'balance': {}, 'aml_groupby_account': {}})
            report_data[parent]['balance'].setdefault(col_key, 0.0)
            report_data[parent]['balance'][col_key] += amount
            _bubble_up(parent, col_key, amount)

        # unpack
        ckey = aml_data['column_group_key']
        acct = aml_data['account_id']
        code = aml_data.get('account_code', '')
        name = aml_data.get('account_name', '')
        amount = aml_data['balance']

        # skip zero
        if self.env.company.currency_id.is_zero(amount):
            return

        # ensure root bucket
        report_data.setdefault(layout_line_id, {
            'balance': {},
            'aml_groupby_account': {},
        })

        # ensure category bucket
        cat = report_data[layout_line_id]['aml_groupby_account'].setdefault(acct, {
            'parent_line_id': layout_line_id,
            'account_id': acct,
            'account_code': code,
            'account_name': name,
            'level': layout_data[layout_line_id]['level'] + 1,
            'balance': {},
            'child_lines': [],  # <-- will fill below
        })

        # accumulate totals
        report_data[layout_line_id]['balance'].setdefault(ckey, 0.0)
        report_data[layout_line_id]['balance'][ckey] += amount

        cat['balance'].setdefault(ckey, 0.0)
        cat['balance'][ckey] += amount

        # bubble up to opening_balance / closing_balance etc.
        _bubble_up(layout_line_id, ckey, amount)

        # ─── for Cash In / Cash Out only ───
        if layout_line_id in ('cash_in', 'cash_out'):
            # 1) find or create the list of company‐level buckets
            companies = cat.setdefault('child_lines', [])

            # 2) find (or make) this aml_data’s parent‐company bucket
            comp_id = aml_data.get('parent_company_id')
            comp_name = aml_data.get('parent_company_name') or 'None'
            comp = next((c for c in companies if c['parent_company_id'] == comp_id), None)
            if not comp:
                comp = {
                    'parent_line_id': layout_line_id,
                    'parent_company_id': comp_id,
                    'parent_company_name': comp_name,
                    'balance': {},  # will accumulate per column
                    'child_lines': [],  # partner‐level goes here
                    'level': layout_data[layout_line_id]['level'] + 1,
                }
                companies.append(comp)

            # 3) accumulate the company’s cash‐flow amount
            comp['balance'].setdefault(ckey, 0.0)
            comp['balance'][ckey] += amount

            # 4) now do the partner‐level grouping under this company
            p_list = comp['child_lines']
            p_id = aml_data.get('partner_id')
            # only create a partner node if we actually have a partner
            if p_id:
                p_name = aml_data.get('partner_name') or 'None'
                part = next((p for p in p_list if p['partner_id'] == p_id), None)
                if not part:
                    part = {
                        'parent_line_id': layout_line_id,  # note: your dynamic code will render it under comp
                        'partner_id': p_id,
                        'partner_name': p_name,
                        'balance': {},
                        'level': comp['level'] + 1,
                    }
                    p_list.append(part)

                # accumulate partner amount
                part['balance'].setdefault(ckey, 0.0)
                part['balance'][ckey] += amount
                # 5) also stash these raw rows for the “last level”
                # part.setdefault('child_lines', []).append({
                #     'parent_line_id': layout_line_id,  # usually layout_line_id or use partner parent
                #     'payment_id': aml_data.get('payment_id'),
                #     'payment_name': aml_data.get('payment_name') or 'Untitled Payment',
                #     'balance': amount,
                #     'level': part['level'] + 1,
                # })
                # ─── payment‐level grouping ───
                payments = part.setdefault('child_lines', [])
                pay_id = aml_data.get('payment_id')
                pay_name = aml_data.get('payment_name') or 'Untitled Payment'
                # find or create this payment bucket
                pay = next((x for x in payments if x['payment_id'] == pay_id), None)
                if not pay:
                    pay = {
                        'parent_line_id': layout_line_id,
                        'payment_id': pay_id,
                        'payment_name': pay_name,
                        'balance': {},  # dict of column_group_key -> amount
                        'level': part['level'] + 1,
                    }
                    payments.append(pay)
                # accumulate into the right period column
                pay['balance'].setdefault(ckey, 0.0)
                pay['balance'][ckey] += amount

    ####
    def _get_account_ids(self, report, options):
        ''' Retrieve all accounts to be part of the cash flow statement and also the accounts making them.

        :param options: The report options.
        :return:        payment_account_ids: A tuple containing all account.account's ids being used in a liquidity journal.
        '''
        # Fetch liquidity accounts:
        # Accounts being used by at least one bank/cash journal.
        selected_journal_ids = [j['id'] for j in report._get_options_journals(options)]

        where_clause = "account_journal.id IN %s" if selected_journal_ids else "account_journal.type IN ('bank', 'cash', 'general')"
        where_params = [tuple(selected_journal_ids)] if selected_journal_ids else []

        self._cr.execute(f'''
            SELECT
                array_remove(ARRAY_AGG(DISTINCT account_account.id), NULL),
                array_remove(ARRAY_AGG(DISTINCT account_payment_method_line.payment_account_id), NULL),
                array_remove(ARRAY_AGG(DISTINCT res_company.account_journal_payment_debit_account_id), NULL),
                array_remove(ARRAY_AGG(DISTINCT res_company.account_journal_payment_credit_account_id), NUll)
            FROM account_journal
            JOIN res_company
                ON account_journal.company_id = res_company.id
            LEFT JOIN account_payment_method_line
                ON account_journal.id = account_payment_method_line.journal_id
            LEFT JOIN account_account
                ON account_journal.default_account_id = account_account.id
                   AND account_account.account_type IN ('asset_cash', 'liability_credit_card')
            WHERE {where_clause}
        ''', where_params)

        res = self._cr.fetchall()[0]
        payment_account_ids = set((res[0] or []) + (res[1] or []) + (res[2] or []) + (res[3] or []))

        if not payment_account_ids:
            return ()

        return tuple(payment_account_ids)

    def _compute_liquidity_balance(self, report, options, currency_table_query, payment_account_ids, date_scope):
        ''' Compute the balance of all liquidity accounts to populate the following sections:
            'Cash and cash equivalents, beginning of period' and 'Cash and cash equivalents, closing balance'.

        :param options:                 The report options.
        :param currency_table_query:    The custom query containing the multi-companies rates.
        :param payment_account_ids:     A tuple containing all account.account's ids being used in a liquidity journal.
        :return:                        A list of tuple (account_id, account_code, account_name, balance).
        '''
        queries = []
        params = []
        if self.pool['account.account'].name.translate:
            lang = self.env.user.lang or get_lang(self.env).code
            account_name = f"COALESCE(account_account.name->>'{lang}', account_account.name->>'en_US')"
        else:
            account_name = 'account_account.name'

        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            tables, where_clause, where_params = report._query_get(column_group_options, date_scope,
                                                                   domain=[('account_id', 'in', payment_account_ids)])

            queries.append(f'''
                SELECT
                    %s AS column_group_key,
                    account_move_line.account_id,
                    account_account.code AS account_code,
                    {account_name} AS account_name,
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                FROM {tables}
                JOIN account_account
                    ON account_account.id = account_move_line.account_id
                LEFT JOIN {currency_table_query}
                    ON currency_table.company_id = account_move_line.company_id
                WHERE {where_clause}
                GROUP BY account_move_line.account_id, account_account.code, {account_name}
            ''')

            params += [column_group_key, *where_params]

        self._cr.execute(' UNION ALL '.join(queries), params)

        return self._cr.dictfetchall()

    # def _compute_cash_flow(self, report, options, currency_table_query,
    #                        payment_account_ids, flow_type):
    #     amount_op = '>' if flow_type == 'in' else '<'
    #     date_from = options['date']['date_from']
    #     date_to = options['date']['date_to']
    #     queries, params = [], []
    #     company_ids = [c['id'] for c in options.get('companies', [])]
    #     if not company_ids:
    #         company_ids = [self.env.company.id]
    #
    #     for col_key, _ in report._split_options_per_column_group(options).items():
    #         queries.append(f"""
    #             SELECT
    #               %s                                    AS column_group_key,
    #               c.id                                  AS account_id,
    #               ''                                    AS account_code,
    #               c.name                                AS account_name,
    #               m.parent_company_id                   AS parent_company_id,
    #               rp.name                               AS parent_company_name,
    #               ap.partner_id                         AS partner_id,
    #               p.name                                AS partner_name,
    #               ap.id                                 AS payment_id,
    #               m.name                                AS payment_name,
    #               SUM(ap.amount_company_currency_signed) AS balance
    #             FROM account_payment ap
    #             JOIN account_move    m  ON ap.move_id = m.id
    #             JOIN res_partner     p  ON ap.partner_id = p.id
    #             LEFT JOIN customer_category c  ON p.customer_category_id = c.id
    #             LEFT JOIN res_partner       rp ON m.parent_company_id = rp.id
    #             LEFT JOIN {currency_table_query}
    #               ON currency_table.company_id = m.company_id
    #             WHERE m.state = 'posted'
    #               AND m.date >= %s
    #               AND m.date <= %s
    #               AND m.company_id IN %s
    #               AND ap.amount_company_currency_signed {amount_op} 0
    #             GROUP BY c.id, c.name, m.parent_company_id, rp.name, ap.partner_id, p.name, ap.id, m.name
    #         """)
    #         # params += [col_key, date_from, date_to]
    #         params += [col_key, date_from, date_to, tuple(company_ids)]
    #
    #     full_query = "\nUNION ALL\n".join(queries)
    #     _logger.debug("Cash flow SQL:\n%s", self._cr.mogrify(full_query, tuple(params)))
    #     _logger.info("full_query:\n%s", full_query)
    #     _logger.info("params:\n%s", params)
    #     self._cr.execute(full_query, params)
    #     return self._cr.dictfetchall()

    def _compute_cash_flow(self, report, options, currency_table_query,
                           payment_account_ids, flow_type):
        amount_op = '>' if flow_type == 'in' else '<'
        queries, params = [], []

        # Build a simple list of company IDs to use in the IN clause
        company_ids = [c['id'] for c in options.get('companies', [])]
        if not company_ids:
            company_ids = [self.env.company.id]
        company_ids_tuple = tuple(company_ids)

        # Loop over each column_group (handles comparison automatically)
        for col_key, col_group in report._split_options_per_column_group(options).items():
            date_from = col_group['date']['date_from']
            date_to   = col_group['date']['date_to']

            queries.append(f"""
                SELECT
                  %s                                    AS column_group_key,
                  c.id                                  AS account_id,
                  ''                                    AS account_code,
                  c.name                                AS account_name,
                  m.parent_company_id                   AS parent_company_id,
                  rp.name                               AS parent_company_name,
                  ap.partner_id                         AS partner_id,
                  p.name                                AS partner_name,
                  ap.id                                 AS payment_id,
                  m.name                                AS payment_name,
                  SUM(ap.amount_company_currency_signed) AS balance
                FROM account_payment ap
                JOIN account_move    m  ON ap.move_id = m.id
                JOIN res_partner     p  ON ap.partner_id = p.id
                LEFT JOIN customer_category c  ON p.customer_category_id = c.id
                LEFT JOIN res_partner       rp ON m.parent_company_id = rp.id
                LEFT JOIN {currency_table_query}
                  ON currency_table.company_id = m.company_id
                WHERE m.state = 'posted'
                  AND m.date >= %s
                  AND m.date <= %s
                  AND m.company_id IN %s
                  AND ap.amount_company_currency_signed {amount_op} 0
                GROUP BY
                  c.id, c.name,
                  m.parent_company_id, rp.name,
                  ap.partner_id, p.name,
                  ap.id, m.name
            """)
            # order of params: col_key, date_from, date_to, (company_ids)
            params += [col_key, date_from, date_to, company_ids_tuple]

        full_query = "\nUNION ALL\n".join(queries)
        self._cr.execute(full_query, params)
        return self._cr.dictfetchall()


    def _get_layout_data(self):
        # Indentation of the following dict reflects the structure of the report.
        return {
            'opening_balance': {'name': _('Cash and cash equivalents, beginning of period'), 'level': 0},
            'cash_in': {'name': _('Cash In'), 'level': 0, },
            'cash_out': {'name': _('Cash OUT'), 'level': 0, },
            'closing_balance': {'name': _('Cash and cash equivalents, closing balance'), 'level': 0},
        }

    def _get_layout_line(self, report, options, layout_line_id, layout_line_data, report_data):
        line_id = report._get_generic_line_id(None, None, markup=layout_line_id)
        unfoldable = 'aml_groupby_account' in report_data[layout_line_id] if layout_line_id in report_data else False

        column_values = []

        for column in options['columns']:
            expression_label = column['expression_label']
            column_group_key = column['column_group_key']

            value = report_data[layout_line_id][expression_label].get(column_group_key,
                                                                      0.0) if layout_line_id in report_data else 0.0

            column_values.append(report._build_column_dict(value, column, options=options))

        return {
            'id': line_id,
            'name': layout_line_data['name'],
            'level': layout_line_data['level'],
            'class': layout_line_data.get('class', ''),
            'columns': column_values,
            'unfoldable': unfoldable,
            'unfolded': line_id in options['unfolded_lines'] or layout_line_data.get('unfolded') or (
                    options.get('unfold_all') and unfoldable),
        }

    def _get_account_line(self, report, options, acc_data):
        parent_line_id = report._get_generic_line_id(None, None, acc_data['parent_line_id'])
        line_id = report._get_generic_line_id('account.account', acc_data['account_id'], parent_line_id=parent_line_id)

        column_values = []

        for column in options['columns']:
            expression_label = column['expression_label']
            column_group_key = column['column_group_key']

            value = acc_data[expression_label].get(column_group_key, 0.0)

            column_values.append(report._build_column_dict(value, column, options=options))

        return {
            'id': line_id,
            'name': f"{acc_data['account_code']} {acc_data['account_name']}",
            'caret_options': 'account.account',
            'level': acc_data['level'],
            'parent_id': parent_line_id,
            'columns': column_values,
        }

    def _get_category_line(self, report, options, cat_data):
        # 1) figure out the parent layout-line’s ID:
        parent_id = report._get_generic_line_id(None, None, markup=cat_data['parent_line_id'])

        # 2) build this category’s own unique ID:
        line_id = report._get_generic_line_id(
            'customer.category',
            cat_data['account_id'],
            parent_line_id=parent_id
        )

        # 3) gather the amounts:
        cols = [
            report._build_column_dict(cat_data['balance'].get(col['column_group_key'], 0.0), col, options=options)
            for col in options['columns']
        ]

        # 4) compute the flags all at once:
        unfoldable = bool(cat_data.get('child_lines'))
        _logger.info(f"--- _unfoldable _get_category_line: {unfoldable} ---")
        unfolded = unfoldable and (
                line_id in options.get('unfolded_lines', [])
                or options.get('unfold_all', False)
        )
        _logger.info(f"--- unfolded _get_category_line: {unfolded} ---")
        category_name = cat_data['account_name'] or 'None'

        return {
            'id': line_id,
            'parent_id': parent_id,
            'name': category_name,
            'level': cat_data['level'],
            'columns': cols,
            'unfoldable': unfoldable,
            'unfolded': unfolded,
        }

    def _get_parent_company_line(self, report, options, data):
        # data['parent_line_id'] is already the category line’s ID
        # It's important to use the actual line ID of the category, not its markup,
        # for parent_id in child lines. In _dynamic_lines_generator, we're passing cat_line['id']
        # which is the correct generated ID for the category line.
        parent_id = data['parent_line_id']
        line_id = report._get_generic_line_id(
            'res.partner',
            data['parent_company_id'],
            parent_line_id=parent_id
        )
        cols = [
            report._build_column_dict(
                data['balance'].get(col['column_group_key'], 0.0),
                col,
                options=options
            )

            for col in options['columns']
        ]
        parent_company_name = data.get('parent_company_name') or 'None'
        # show a caret only if there are partners under this company
        has_partners = bool(data.get('child_lines'))
        unfolded = has_partners and (line_id in options.get('unfolded_lines', []))
        _logger.debug(f"Company {parent_company_name} unfoldable={has_partners} unfolded={unfolded}")
        return {
            'id': line_id,
            'parent_id': parent_id,
            'level': data.get('level', 2),
            'name': parent_company_name,
            'columns': cols,
            'unfoldable': has_partners,
            'unfolded': unfolded,
        }

    def _get_partner_line(self, report, options, data):
        parent_id = data['parent_line_id']
        line_id = report._get_generic_line_id(
            'res.partner',
            data['partner_id'],
            parent_line_id=parent_id
        )
        cols = [
            report._build_column_dict(
                data['balance'].get(col['column_group_key'], 0.0),
                col,
                options=options
            )

            for col in options['columns']
        ]
        partner_name = data.get('partner_name') or 'None'
        # show a caret only if there are partners under this company
        has_payments = bool(data.get('child_lines'))
        unfolded = has_payments and (line_id in options.get('unfolded_lines', []))
        _logger.debug(f"Partner {partner_name} unfoldable={has_payments} unfolded={unfolded}")
        return {
            'id': line_id,
            'parent_id': parent_id,
            'level': data.get('level', 2),
            'name': partner_name,
            'columns': cols,
            'unfoldable': has_payments,
            'unfolded': unfolded,
        }

    def _get_payment_line(self, report, options, data):
        line_id = report._get_generic_line_id(
            'account.payment',  # or 'account.move' if you want the move id
            data['payment_id'],
            parent_line_id=data['parent_line_id']
        )
        cols = [
            report._build_column_dict(
                data['balance'].get(col['column_group_key'], 0.0),
                col,
                options=options
            ) for col in options['columns']
        ]
        return {
            'id': line_id,
            'parent_id': data['parent_line_id'],
            'level': data['level'],
            'name': data['payment_name'],
            'columns': cols,
            'caret_options': 'account.payment',
        }
