{
    'name': 'Custom Payslip',
    'summary': 'HR Custom Payslip',
    'description': """""",
    'category': 'Hr',

    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'license': 'LGPL-3',
    'application': False,

    'sequence': '-150',
    'version': '19.0.1.0.0',
    'depends': ['hr_payroll', 'erpc_hr_payroll_extension', 'hr'],
    'data': [
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
    ],
}
