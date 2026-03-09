{
    'name': 'Landed Cost Entry',
    'version': '19.0.1.0.0',
    'summary': 'Landed Cost Entry',
    'category': 'Landed Cost Entry',
    'description': """ Landed Cost Entry """,
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'category': 'Accounting',
    'depends': ['account', 'base', 'stock_landed_costs','mrp_landed_costs','stock'],
    'sequence': "-400",
    'data': [
        'security/group.xml',
        # 'security/ir.model.access.csv',
        # 'views/landed_account_move.xml',
    ],

    'application': True,
    'auto install': False,
    'license': 'LGPL-3',
}