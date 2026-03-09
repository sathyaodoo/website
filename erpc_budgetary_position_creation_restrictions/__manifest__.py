{
    'name': 'ERPC Budgetary Positions Creation & Restrictions',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'author': 'ERP Cloud S.A.R.L',
    'sequence': -100,
    'summary': 'ERPC Budgetary Positions Creation & Restrictions',
    'description': """ERPC Budgetary Positions Creation & Restrictions,""",
    'depends': ['base', 'account', 'account_budget', 'erpc_accounting_financial_groups'],
    'data': [
        'security/security.xml',
        # 'views/view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
