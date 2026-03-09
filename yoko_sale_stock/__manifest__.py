# -*- coding: utf-8 -*-
{
    'name': "Yoko Sale/Stock Customizations",

    'summary': """Edit/Create Sale/Stock Related Models""",

    'description': """
        - Promotional Sale Order
    """,

    'author': "Intalio",
    'website': "http://www.yourcompany.com",
    'category': 'Stock',
    'version': '19.0.1.0.0',
    'license': 'OPL-1',

    'depends': ['yoko_stock', 'yoko_security_custom'],

    'data': [
        'security/rules.xml',
        # # 'data/data.xml',
        'views/sale_order.xml',
    ],
}
