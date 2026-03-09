{
    'name': 'ERPC Automated Yearly Discount Transfer Entry',
    "version": "19.0.1.0.0",
    'category': 'Accounting',
    'author': 'ERP Cloud S.A.R.L',
    'sequence': -100,
    'summary': 'ERPC Automated Yearly Discount Transfer Entry',
    'description': """ Automate a transaction when we confirm the deferral bill of yearly discount to shift from 
    payable account to receivable in order to show in balance sheet as a deduction in balance sheet and show in 
    the bill beside deferral entries the shift entry,""",
    'depends': ['base', 'account'],
    'data': [
        # 'views/view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
