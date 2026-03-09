{
    'name': 'ERPC Deferrals Automatic Reconcile',
    'sequence': -102,
    'category': 'Accounting',
    'summary': 'ERPC Deferrals Automatic Reconcile',
    'description': """ Reconcile 472101 account in of main deferral entries with the other related entries
    upon automatically posting of each entry(month) """,
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'base', 'account', 'account_accountant',
    ],
    'data': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
