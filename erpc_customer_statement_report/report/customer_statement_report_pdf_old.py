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
            sql = """select  aml.currency_id,sum(case when aml.debit  != 0.0 and aml.currency_id is  not null then aml.amount_currency 
                                when aml.debit  != 0.0 and aml.currency_id is null then aml.debit else 0.0 end) as debit,
                                abs(sum(case when aml.credit  != 0.0 and aml.currency_id is not null then aml.amount_currency
                                when aml.credit  != 0.0 and aml.currency_id is null then aml.credit else 0.0 end )) as credit 
                                from  account_move_line aml
                                inner join res_partner rp on rp.id = aml.partner_id %s %s %s %s
                                inner join account_move am on am.id = aml.move_id %s %s
                                group by aml.partner_id,aml.currency_id
                               """ % (
                partner_domain, currency_domain, date_domain, journal_domain, company_domain, target_move)
            self._cr.execute(sql)
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
                    select am.name jname,am.ref as ref,aj.code as code ,aml.date, aml.partner_id, aml.id ,aml.name,
                    case when aml.debit  != 0.0 and aml.currency_id is  not null then aml.amount_currency 
                    when aml.debit  != 0.0 and aml.currency_id is null then aml.debit else 0.0 end as debit
                    ,case when aml.credit  != 0.0 and aml.currency_id is not null then -1 * aml.amount_currency
                    when aml.credit  != 0.0 and aml.currency_id is null then aml.credit else 0.0 end as credit
                    ,case when aml.currency_id is  not null then aml.amount_residual_currency 
                    when aml.currency_id is null then aml.amount_residual else 0.0 end as due
                    ,aml.currency_id,aml.amount_currency from 
                     res_partner rp 
                    inner join account_move_line aml on rp.id = aml.partner_id %s %s %s %s
                    inner join account_move am on am.id = aml.move_id %s %s
                    inner join account_journal aj on aj.id = am.journal_id
                    order by aml.date

     """ % (partner_domain, currency_domain, journal_domain, date_domain, company_domain, target_move)
        else:
            sql = """  
                    select am.name jname,am.ref as ref,aj.code as code ,aml.date, aml.partner_id, aml.id ,aml.name,
                    case when aml.debit  != 0.0 and aml.currency_id is  not null then aml.amount_currency 
                    when aml.debit  != 0.0 and aml.currency_id is null then aml.debit else 0.0 end as debit
                    ,case when aml.credit  != 0.0 and aml.currency_id is not null then -1 * aml.amount_currency
                    when aml.credit  != 0.0 and aml.currency_id is null then aml.credit else 0.0 end as credit
                    ,case when aml.currency_id is  not null then aml.amount_residual_currency 
                    when aml.currency_id is null then aml.amount_residual else 0.0 end as due
                    ,aml.currency_id,aml.amount_currency from 
                     res_partner rp 
                    inner join account_move_line aml on rp.id = aml.partner_id %s %s %s %s
                    inner join account_move am on am.id = aml.move_id %s %s
                    inner join account_journal aj on aj.id = am.journal_id
                    WHERE aml.amount_residual != 0
                    order by aml.date

                 """ % (partner_domain, currency_domain, journal_domain, date_domain, company_domain, target_move)
        self._cr.execute(sql)
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
