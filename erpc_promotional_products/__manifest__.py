{
    'name': 'Promotional Products',
    'version': '19.0.1.0.0',
    'summary': 'Product Size',
    'category': '',

    'description': """ PO From Requisition lines """,
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['base','sale_stock', 'product', 'sale', 'yoko_customization','sale','yoko_security_custom','erpc_inventory_apply'],
    'sequence': "-400",

    'data': [
        'security/security.xml',
        'views/promo.xml',
    ],

    'application': True,
    'auto install': False,
    'license': 'LGPL-3',
}