{
    'name': 'Hr Payroll Extension',
    'version': '19.0.1.0.0',
    'description': 'payroll extension features',
    'category': 'Generic Modules/Human Resources',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['base', 'hr', 'hr_payroll',],
    'application': True,
    'images': ['static/description/banner.png'],
    'data': [
        'data/data_payroll.xml',
        'data/hr.salary.rule.category.csv',
        'views/menu.xml',
    ],
    'license': 'OPL-1',
}
