{
    'name': 'Brand Target Table',
    'version': '19.0.1.0.0',
    'summary': 'Brand Target Table',
    'category': '',

    'description': """ Brand Target Table """,
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['base', 'stock', 'product', 'sale', 'yoko_stock'],
    'sequence': "-400",

    'data': [
        # 'security/ir.model.access.csv',
        # 'views/brand_target_view.xml',
    ],

    'application': True,
    'auto install': False,
    'license': 'LGPL-3',
}