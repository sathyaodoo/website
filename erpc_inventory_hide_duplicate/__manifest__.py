{
    'name': 'ERPC Physical Inventory Hide Duplicate',
    'sequence': -102,
    'category': 'Accounting',
    'description': """ ERPC Physical Inventory Hide Duplicate """,
    'summary': 'ERPC Physical Inventory Hide Duplicate',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'base', 'stock', 'web'
    ],
    'data': [
        'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,


}