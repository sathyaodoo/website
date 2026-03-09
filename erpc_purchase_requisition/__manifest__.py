{
    'name': 'PO From Requisition lines',
    'version': '19.0.1.0.0',
    'summary': 'PO From Requisition lines',
    'category': 'PO From Requisition lines',

    'description': """ PO From Requisition lines """,
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'category': 'Purchase',
    'depends': ['base', 'stock', 'purchase', 'purchase_requisition'],
    'sequence': "-400",

    'data': [
        'views/purchase_requisition.xml',
    ],

    'application': True,
    'auto install': False,
    'license': 'LGPL-3',
}