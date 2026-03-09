{
    'name': 'Remove Force Balance from Payment Wizard',
    'sequence': -102,
    'category': 'Accounting',
    'description': """ Remove froce balance when register a payment in foreign currency (process of odoo 16) """,
    'summary': 'Remove Force Balance from Payment Wizard',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'base', 'account',
    ],
    'data': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,


}