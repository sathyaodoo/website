# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class PayrollReport(models.Model):
    _name = "payroll.report"
    _description = "Payroll Report"
    _auto = False
    _rec_name = 'employee'
    #_order = 'date_from desc'

    @api.model
    def _get_done_states(self):
        return ['done', 'paid']

    employee_id = fields.Char('Employee ID', readonly=True)
    employee = fields.Many2one('hr.employee', 'Employee', readonly=True)
    date_from = fields.Date('From', readonly=True)
    date_to = fields.Date('To', readonly=True)
    job_position = fields.Char('Job', readonly=True)
    department = fields.Many2one('hr.department', 'Department', readonly=True)
    #TODO : To che check the res.branch model in 17 to 19
    branch = fields.Many2one('res.users', 'Branch', readonly=True) 
    # basic_salary = fields.Float('Basic Salary', readonly=True)
    overtime = fields.Float('Overtime', readonly=True) 
    undertime = fields.Float('Undertime', readonly=True)  
    bonus = fields.Float('Bonus', readonly=True)  
    commission = fields.Float('Commission', readonly=True)  
    ios_commission = fields.Float('IOS Commission', readonly=True)
    company_loan = fields.Float('Company Loan', readonly=True)
    retail_loan = fields.Float('Retail Loan', readonly=True)
    insurance = fields.Float('Insurance', readonly=True) 
    warning = fields.Float('Warning', readonly=True) 
    deduction = fields.Float('Deduction', readonly=True)  
    salary = fields.Float('Salary', readonly=True)
    net_salary = fields.Float('Net Salary', readonly=True)
    rounded_usd = fields.Float('Round USD', readonly=True)
    rounded_lbp = fields.Float('Rounded LBP', readonly=True)
    rounded_full = fields.Float('Deduction', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Rejected'),
        ], string='Status', readonly=True)

    def _with_payroll(self):
        return ""

    def _select_payroll(self):
        select_ = f"""
                MIN(p.id) AS id,
                e.name AS employee_id, 
                p.date_from AS date_from, 
                p.date_to AS date_to, 
                e.id AS employee,
                j.name AS job_position              
            """

        additional_fields_info = self._select_additional_fields()
        template = """,
            %s AS %s"""
        for fname, query_info in additional_fields_info.items():
            select_ += template % (query_info, fname)

        return select_

    def _case_value_or_one(self, value):
        return f"""CASE COALESCE({value}, 0) WHEN 0 THEN 1.0 ELSE {value} END"""

    def _select_additional_fields(self):
        """Hook to return additional fields SQL specification for select part of the table query.

        :returns: mapping field -> SQL computation of field, will be converted to '_ AS _field' in the final table definition
        :rtype: dict
        """
        return {}

    def _from_payroll(self):
        return """
            hr_payslip_line p
            LEFT JOIN hr_employee e ON e.id=p.employee_id
            LEFT JOIN hr_department d ON d.id=e.department_id
            LEFT JOIN hr_job j ON j.id=e.job_id
            """

    def _where_payroll(self):
        return """"""

    def _group_by_payroll(self):
        return """
            p.date_from,
            p.date_to,
            e.name,
            e.id,
            j.name
            """

    def _query(self):
        with_ = self._with_payroll()
        return f"""
            {"WITH" + with_ + "(" if with_ else ""}
            SELECT {self._select_payroll()}
            FROM {self._from_payroll()}
            GROUP BY {self._group_by_payroll()}
            {")" if with_ else ""}
        """

    @property
    def _table_query(self):
        return self._query()
