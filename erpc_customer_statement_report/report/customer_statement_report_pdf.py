# -*- coding: utf-8 -*-

from odoo import api, models
import logging

_log = logging.getLogger(__name__)


class PartnerLedgerForeignCurrency(models.AbstractModel):
    _name = 'report.erpc_customer_statement_report.partnerledger'

    def get_init(self, data, partner_id):
        init_dic = {}
        if data['form']['date_from'] and data['form']['with_null_amount_residual'] == True:
            company_domain = ' and am.company_id = %d ' % self.env.user.company_id.id
            partner_domain = ' and aml.partner_id = %d ' % partner_id.id
            date_domain = """ and aml.date < '%s' """ % data['form']['date_from']
            curr_obj = self.env['res.currency']
            currency_domain = ''
            if data['form']['currency_id'] and data['form']['currency_id'][
                0] == self.env.user.company_id.currency_id.id:
                currency_domain = ' and (aml.currency_id is null or aml.currency_id = %d)' % self.env.user.company_id.currency_id.id
            elif data['form']['currency_id']:
                currency_domain = ' and aml.currency_id = %d ' % data['form']['currency_id'][0]
            target_move = ''
            if data['form']['target_move'] == 'posted':
                target_move = " and am.state = 'posted' "
            if data['form']['account_type'] == 'payable':
                journal_domain = " and aml.account_id = %d " % partner_id.property_account_payable_id.id
            elif data['form']['account_type'] == 'customer':
                journal_domain = " and aml.account_id = %d " % partner_id.property_account_receivable_id.id
            else:
                journal_domain = " and aml.account_id in (%d,%d)  " % (
                    partner_id.property_account_receivable_id.id, partner_id.property_account_payable_id.id)
            ini_domain = """ and aml.date < '%s' """ % data['form']['date_from']
            sql = """
                SELECT
                    aml.currency_id,
                    -- debit in display currency
                    SUM(
                        CASE
                            -- foreign currency: use positive amount_currency
                            WHEN aml.currency_id IS NOT NULL
                                 AND aml.currency_id <> company.currency_id
                                THEN GREATEST(aml.amount_currency, 0)
                            -- company currency: use debit
                            ELSE aml.debit
                        END
                    ) AS debit,
                    -- credit in display currency
                    SUM(
                        CASE
                            -- foreign currency: use negative amount_currency as credit (absolute)
                            WHEN aml.currency_id IS NOT NULL
                                 AND aml.currency_id <> company.currency_id
                                THEN ABS(LEAST(aml.amount_currency, 0))
                            -- company currency: use credit
                            ELSE aml.credit
                        END
                    ) AS credit
                FROM account_move_line aml
                INNER JOIN account_move am
                    ON am.id = aml.move_id %s %s
                INNER JOIN res_company company
                    ON company.id = am.company_id
                INNER JOIN res_partner rp
                    ON rp.id = aml.partner_id %s %s %s %s
                GROUP BY
                    aml.currency_id
            """ % (
                company_domain,  # e.g. " AND am.company_id = 1"
                target_move,  # e.g. " AND am.state = 'posted'"
                partner_domain,  # e.g. " AND aml.partner_id = 9205"
                currency_domain,  # if you filter by aml.currency_id
                date_domain,  # e.g. " AND aml.date < '2025-01-01'"
                journal_domain,  # e.g. " AND aml.account_id IN (115,101)"
            )

            self._cr.execute(sql)
            _log.info(f'\n\n\n\n*****sql****get_init***{sql}\n\n\n\n.')
            dic = {}
            lines_init = self._cr.dictfetchall()
            for i in lines_init:
                dic[curr_obj.browse(i['currency_id'] or self.env.user.company_id.currency_id.id)] = {
                    'debit': i['debit'], 'credit': i['credit']}

            return dic
        else:
            return {}

    def get_lines(self, data, partner_id):
        acc_type = []
        if data['form']['account_type'] == 'payable':
            acc_type = ['liability_payable']
        elif data['form']['account_type'] == 'customer':
            acc_type = ['asset_receivable']
        else:
            acc_type = ['asset_receivable', 'liability_payable']

        _log.info(f'\n\n\n\n*****acc_type pdf*******{acc_type}\n\n\n\n.')
        account_obj = self.env['account.account']

        payable_receivable = account_obj.search([('account_type', 'in', acc_type)])
        payable_receivable_ids = (0)
        if payable_receivable:
            if len(payable_receivable) > 1:
                payable_receivable_ids = tuple(payable_receivable.ids)
            else:
                payable_receivable_ids = '(' + str(payable_receivable.id) + ')'

        journal_domain = ' and aml.account_id in %s ' % str(payable_receivable_ids)

        company_domain = ' and am.company_id = %d ' % self.env.user.company_id.id
        date_domain = ''
        if data['form']['date_from']:
            date_domain += """ and aml.date >= '%s' """ % data['form']['date_from']
        if data['form']['date_to']:
            date_domain += """ and aml.date <= '%s' """ % data['form']['date_to']
        target_move = ''
        if data['form']['target_move'] == 'posted':
            target_move = " and am.state = 'posted' "
        currency_domain = ''
        if data['form']['currency_id']:
            if data['form']['currency_id'] and data['form']['currency_id'][
                0] == self.env.user.company_id.currency_id.id:
                currency_domain = ' and (aml.currency_id is null or aml.currency_id = %d) ' % self.env.user.company_id.currency_id.id
            else:
                currency_domain = ' and aml.currency_id = %d ' % data['form']['currency_id'][0]

        partner_domain = ' and aml.partner_id = %d ' % partner_id.id

        if data['form']['with_null_amount_residual'] == True:
            sql = """  
                SELECT
                    am.name AS jname,
                    am.ref AS ref,
                    aj.code AS code,
                    aml.date,
                    aml.partner_id,
                    aml.id,
                    aml.name,
            
                    -- Debit: company currency -> aml.debit, foreign currency -> aml.amount_currency
                    CASE
                        WHEN aml.debit != 0.0
                             AND aml.currency_id IS NOT NULL
                             AND aml.currency_id <> company.currency_id
                            THEN aml.amount_currency
                        WHEN aml.debit != 0.0
                             AND (aml.currency_id IS NULL
                                  OR aml.currency_id = company.currency_id)
                            THEN aml.debit
                        ELSE 0.0
                    END AS debit,
            
                    -- Credit: company currency -> aml.credit, foreign currency -> -1 * aml.amount_currency
                    CASE
                        WHEN aml.credit != 0.0
                             AND aml.currency_id IS NOT NULL
                             AND aml.currency_id <> company.currency_id
                            THEN -1 * aml.amount_currency
                        WHEN aml.credit != 0.0
                             AND (aml.currency_id IS NULL
                                  OR aml.currency_id = company.currency_id)
                            THEN aml.credit
                        ELSE 0.0
                    END AS credit,
            
                    -- Due: company currency -> amount_residual, foreign currency -> amount_residual_currency
                    CASE
                        WHEN aml.currency_id IS NOT NULL
                             AND aml.currency_id <> company.currency_id
                            THEN aml.amount_residual_currency
                        WHEN aml.currency_id IS NULL
                             OR aml.currency_id = company.currency_id
                            THEN aml.amount_residual
                        ELSE 0.0
                    END AS due,
            
                    aml.currency_id,
                    aml.amount_currency
            
                FROM res_partner rp 
                INNER JOIN account_move_line aml
                    ON rp.id = aml.partner_id %s %s %s %s
                INNER JOIN account_move am
                    ON am.id = aml.move_id %s %s
                INNER JOIN res_company company
                    ON company.id = am.company_id
                INNER JOIN account_journal aj
                    ON aj.id = am.journal_id
                ORDER BY aml.date

            """ % (partner_domain, currency_domain, journal_domain, date_domain, company_domain, target_move)
        else:
            sql = """  
                    SELECT
                    am.name AS jname,
                    am.ref AS ref,
                    aj.code AS code,
                    aml.date,
                    aml.partner_id,
                    aml.id,
                    aml.name,
            
                    -- Debit: company currency -> aml.debit, foreign currency -> aml.amount_currency
                    CASE
                        WHEN aml.debit != 0.0
                             AND aml.currency_id IS NOT NULL
                             AND aml.currency_id <> company.currency_id
                            THEN aml.amount_currency
                        WHEN aml.debit != 0.0
                             AND (aml.currency_id IS NULL
                                  OR aml.currency_id = company.currency_id)
                            THEN aml.debit
                        ELSE 0.0
                    END AS debit,
            
                    -- Credit: company currency -> aml.credit, foreign currency -> -1 * aml.amount_currency
                    CASE
                        WHEN aml.credit != 0.0
                             AND aml.currency_id IS NOT NULL
                             AND aml.currency_id <> company.currency_id
                            THEN -1 * aml.amount_currency
                        WHEN aml.credit != 0.0
                             AND (aml.currency_id IS NULL
                                  OR aml.currency_id = company.currency_id)
                            THEN aml.credit
                        ELSE 0.0
                    END AS credit,
            
                    -- Due: company currency -> amount_residual, foreign currency -> amount_residual_currency
                    CASE
                        WHEN aml.currency_id IS NOT NULL
                             AND aml.currency_id <> company.currency_id
                            THEN aml.amount_residual_currency
                        WHEN aml.currency_id IS NULL
                             OR aml.currency_id = company.currency_id
                            THEN aml.amount_residual
                        ELSE 0.0
                    END AS due,
            
                    aml.currency_id,
                    aml.amount_currency
            
                FROM res_partner rp 
                INNER JOIN account_move_line aml
                    ON rp.id = aml.partner_id %s %s %s %s
                INNER JOIN account_move am
                    ON am.id = aml.move_id %s %s
                INNER JOIN res_company company
                    ON company.id = am.company_id
                INNER JOIN account_journal aj
                    ON aj.id = am.journal_id
                WHERE aml.amount_residual != 0
                ORDER BY aml.date

            """ % (partner_domain, currency_domain, journal_domain, date_domain, company_domain, target_move)
        self._cr.execute(sql)
        _log.info(f'\n\n\n\n*****sql****get_lines***{sql}\n\n\n\n.')
        lines = self._cr.dictfetchall()
        dic = {}
        cu = data['form']['currency_id']
        curr_obj = self.env['res.currency']
        for line in lines:
            line['currency_id'] = curr_obj.browse(line['currency_id']) if line[
                'currency_id'] else self.env.user.company_id.currency_id
            if line['currency_id'] in dic and line['partner_id']:
                dic[line['currency_id']].extend([line])
            else:
                dic[line['currency_id']] = [line] if line['partner_id'] else []
        bal = self.get_init(data, partner_id)
        for i in bal.keys():
            if i not in dic:
                dic.update({i: []})
        final_list = []
        for k, v in dic.items():
            final_list.append(
                {'bal': bal[k] if k in bal else {'debit': 0.0, 'credit': 0.0}, 'cu': k, 'lines': v})
        return final_list

    @api.model
    def _get_report_values(self, docids, data=None):
        parent_id = self.env['res.partner'].browse(data['form']['active_ids'])
        child_ids = self.env['res.partner'].search([('parent_id', 'in', parent_id.ids)])
        new_partner_ids = [parent.id for parent in parent_id] + [child.id for child in child_ids]
        _log.info(f'\n\n\n\n*****new_partner_ids*******{new_partner_ids}\n\n\n\n.')
        # all_partners = parent_id + child_ids
        due_child_ids = child_ids.filtered(lambda record: record.total_due)
        all_partners = parent_id + due_child_ids
        # due_partners = all_partners.filtered(lambda record: record.total_due)
        _log.info(f'\n\n\n\n*****all_partners*******{all_partners}\n\n\n\n.')
        return {
            'doc_ids': docids,
            # 'docs': partner_ids,
            'docs': all_partners,
            'data': data,
            'get_lines': self.get_lines,
            'get_init': self.get_init

        }
