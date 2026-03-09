{
    'name': 'Custom Payroll',
    'summary': 'HR Custom Payroll',
    'description': """Payroll custom for leb and usd """,
    'category': 'Hr',

    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'license': 'LGPL-3',
    'application': False,

    'sequence': '-150',
    'version': '19.0.1.0.0',
    'depends': ['hr_payroll', 'erpc_hr_payroll_extension', 'erpc_contract_history', 'erpc_employee_fields_positions'],
    'data': [
        'security/ir.model.access.csv',
        #'data/hr.salary.rule.csv',
        'views/hr_contract_views.xml',
        # 'views/hr_payslip_employees_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_employee_view.xml',
        'report/payroll_report_views.xml'
    ],
}
