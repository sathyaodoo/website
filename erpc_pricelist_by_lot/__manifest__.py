{
    'name': 'Pricelist Filtering by Lot',
    'sequence': -102,
    'category': 'Sales/Sales',
    'description': 'Filter pricelist items by product lot numbers',
    'summary': 'Filter pricelist items by product lot numbers',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'ERP Cloud S.A.R.L',
    'website': 'https://www.erpcloudllc.com/',
    'depends': [
        #TODO: To add  industry_fsm_stock
        'product','sale' ,'sale_order_lot_selection'
        # 'product','sale' ,'sale_order_lot_selection', 'industry_fsm_stock'
    ],
    'data': [
        # 'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}