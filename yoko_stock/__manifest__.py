# -*- coding: utf-8 -*-
{
    'name': "Yoko Stock Customizations",
    'summary': """Edit/Create Stock Related Models""",
    'description': """
        - Products \n
        - Stock Location \n
        - Stock Quant. \n 
        - Stock Move Line \n 
    """,
    'author': "Intalio",
    'website': "http://www.yourcompany.com",
    'category': 'Stock',
    'version': '19.0.1.0.0',
    'license': 'OPL-1',
    'depends': ['base', 'sale_stock', 'yoko_security_custom', 'stock', 'stock_barcode', 'product'],
    'data': [
        # # 'security/rules.xml',
        'data/data.xml',
        # # 'views/stock_valuation.xml',
        'views/stock_location.xml',
        'views/stock_move_line.xml',
        'views/stock_quant.xml',
        # # 'views/product_brand.xml',
        # # 'views/product_categories.xml',
        'views/product_category.xml',
        # # 'views/product_family.xml',
        # # 'views/product_pattern.xml',
        # # 'views/product_series.xml',
        # # 'views/product_type.xml',
        # # 'views/product_size.xml',
        # 'views/product_template.xml',
        # 'views/product_product.xml',
    ],
}
