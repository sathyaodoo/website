{
    'name': 'Product - Can be Fixed Asset',
    'sequence': -102,
    'category': 'Product',
    'description': """ Add can be fixed asset to product """,
    'summary': 'Product - Can be Fixed Asset',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        'base', 'product', 'account', 'yoko_stock'
    ],
    'data': [
        'views/product.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,


}