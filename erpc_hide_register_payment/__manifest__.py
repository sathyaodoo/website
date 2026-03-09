{
    'name': 'Hide Register Payment',
    'version': '19.0.1.0.0',
    'summary': '',
    'description': """
        """,
    'category': 'Accounting',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base','account', 'account_accountant'
    ],
    'data': [
        'security/security.xml',
        'views/account_move_view.xml',
    ],

    'images': [
      'static/description/icon.png'
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
