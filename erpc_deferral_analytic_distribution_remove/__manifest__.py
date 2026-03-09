{
    'name': 'ERPC Deferrals Remove Analytic Distribution',
    'sequence': -102,
    'category': 'Accounting',
    'summary': 'ERPC Deferrals Remove Analytic Distribution',
    'description': """ Remove analytic distribution from accounts 
    not start with 6 or 7 upon creation of deferrals entries, Allow deferrals bills with income accounts """,
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'base', 'account', 'account_accountant', 'account_reports',
    ],
    'data': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
