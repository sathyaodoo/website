{
    'name': 'Stock Reservation Management',
    'version': '19.0.1.0.0',
    'summary': 'Manage Stock Reservation',
    'description': """
        Helps you to manage stock reservation.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': [
        'base','stock_reserve',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/erpc_stock_reservation.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
