{
    'name': 'ERPC Automated Stock Variation Entries',
    'sequence': -102,
    'category': 'Stock Accounting',
    'description': """ ERPC Automated Stock Variation Entries, """,
    'summary': 'ERPC Automated Stock Variation Entries',
    "version": "19.0.1.0.0",
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'base', 'account', 'stock', 'stock_account', 'analytic', 'stock_accountant', 'yoko_stock', 'erpc_lot_discount',
    ],
    'data': [
        'views/views.xml',
        # 'data/ir_cron_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}