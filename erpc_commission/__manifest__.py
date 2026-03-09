{
    'name': 'Commission Management',
    'version': '19.0.1.0.0',
    'summary': 'Manage Commission Requests',
    'description': """
        Helps you to manage Commission of your company's staff.
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
        'views/hr_comission_seq.xml',
        'data/salary_rule_comission.xml',
        'views/hr_comission.xml',
        'views/hr_payroll.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
