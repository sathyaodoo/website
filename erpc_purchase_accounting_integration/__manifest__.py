{
    'name': 'ERPC Accounting | Stock - Relation between Purchase & Accounting',
    'version': '19.0.1.0.0',
    'summary': 'Purchase Accounting Integration',
    'category': '',

    'description': """ Purchase Accounting Integration """,
    'author': 'ERP Cloud S.A.R.L',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['base','purchase', 'erpc_purchase_requisition', 'purchase_requisition', 'erpc_purchase_blanket_order'],
    'sequence': "-400",

    'data': [
        # 'views/po_lines_view.xml',
        # 'views/purchase_view.xml',
    ],

    'application': True,
    'auto install': False,
    'license': 'LGPL-3',
}