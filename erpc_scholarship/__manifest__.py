{
    'name': 'Scholarship Management',
    'version': '19.0.1.0.0',
    'summary': '''Helps you to manage Scholarship of your company's staff.''',
    'description': """
        """,
    'category': 'Generic Modules/Human Resources',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'erpc_hr_payroll_extension',
    ],
    'data': [
        'data/salary_rule_scholarship.xml',
        'security/security.xml',
        'views/hr_payroll.xml',
        'views/hr_scholarship_seq.xml',
        'views/hr_scholarship.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
