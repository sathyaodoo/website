{
    'name': 'Sale - Restrict price unit',
    'sequence': -102,
    'category': 'Sales',
    'description': 'Sale - Restrict price unit',
    'summary': 'Sale - Restrict price unit',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'base', 'sale', 'yoko_sale_stock',
    ],
    'data': [
        'security/security.xml',
        'views/view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}