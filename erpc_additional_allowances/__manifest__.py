{
    'name': 'Additional Allowances Management',
    "version": "19.0.1.0.0",
    'summary': 'Manage Commission Requests',
    'description': """
        Helps you to manage additional allowances of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'erpc_hr_payroll_extension',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        # 'views/hr_additional_allowances_seq.xml',
        # 'data/salary_rule_additional_allowances.xml',
        # 'views/hr_additional_allowances.xml',
        # 'views/hr_payroll.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
