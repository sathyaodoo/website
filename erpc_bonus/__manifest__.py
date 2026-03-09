{
    'name': 'Bonus Management',
    'version': '19.0.1.0.0',
    'summary': 'Manage Commission Requests',
    'description': """
        Helps you to manage Bonus of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'erpc_hr_payroll_extension',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_bonus_seq.xml',
        'data/salary_rule_bonus.xml',
        'views/hr_bonus.xml',
        'views/hr_payroll.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
