{
    'name': 'Qty 0 at return',
    'version': '19.0.0.0.0',                     # Changed from 17.0.0.0.0
    'summary': 'Qty 0 at Return Level',
    'description': """
        Qty 0 at Return Level
        """,
    'category': 'Accounting',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base',
        'account',
        'sale',
        'loyalty',                                # Confirm this module still exists in Odoo 19
        'sale_loyalty',                           # Confirm this module still exists in Odoo 19
        'yoko_customization'                       # Custom module, ensure it is compatible
    ],
    'data': [
        # 'views/view.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}