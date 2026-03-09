{
    'name': 'Defaults Journal in Bekaa Payments',
    'version': '19.0.1.0.0',
    'summary': 'Defaults Journal in Bekaa Payments',
    'description': """Set default journal for customer/vendor payments in Bekaa Branch""",
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base',
        'account',
        'account_accountant',
        # 'yoko_customization',
    ],
    'data': [
        'security/security.xml',
        # 'views/view.xml',
    ],
    'license': 'OPL-1',
}
