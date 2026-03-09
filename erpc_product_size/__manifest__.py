{
    'name': 'Product Size',
    'version': '19.0.1.0.0',
    'summary': 'Product Size',
    'category': '',

    'description': """ PO From Requisition lines """,
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['base', 'stock', 'product', 'sale', 'account', 'approvals','purchase','approvals_purchase'],
    'sequence': "-400",

    'data': [
        'views/views.xml',
        # 'security/ir.model.access.csv',
        'security/groups.xml',
    ],

    'application': True,
    'auto install': False,
    'license': 'LGPL-3',
}