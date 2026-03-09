{
    "name": "Yoko Customization",
    "summary": """Yoko Customization""",
    "description": """Yoko Customization""",
    "author": "Intalio",
    "category": "Uncategorized",
    "license": "LGPL-3",
    "version": "19.0.1.0.0",
    # TODO: depend on yoko_sale_stock, to use is_promo/advertising in Multiple Products, once separated dependency can be removed
    "depends": [
        "account_reports",
        "account_accountant",
        "sale_management",
        "sale",
        "sales_team",
        "sale_margin",
        "base",
        "account",
        "contacts",
        "product",
        "purchase",
        "delivery",
        "stock",
        "yoko_security_custom",
        "yoko_sale_stock",
        "erpc_invoice_report_discount",
    ],
    "data": [
        # # 'wizard/multi_product.xml',
        # # 'wizard/multi_selection.xml',
        # 'reports/paper_formats.xml',
        # 'reports/invoice_custom_report.xml',
        # 'reports/invoice_main_report.xml',
        # # 'reports/invoice_template.xml', # it didn't have action report
        # 'reports/invoice_template_JP.xml',  # has no effect, it is the same as invoice_template_three.xml
        # 'reports/invoice_template_JP_without_disc.xml',
        # # 'reports/invoice_template_three.xml',
        # # 'reports/invoice_template_two.xml', # it didn't have action report
        # 'reports/order_template.xml',
        # 'reports/report.xml',
        # # 'views/account.xml',
        "views/account_move.xml",
        "views/account_move_view.xml",
        # # 'views/brand_product.xml', # TODO: can be removed after installing yoko_stock
        # # 'views/business_type.xml',
        # # 'views/cancel_so.xml',
        # # 'views/classifications.xml', # TODO: can be removed after installing yoko_stock
        "views/contact_fields.xml",
        # # 'views/customer_category.xml',
        "views/customer_payment.xml",
        # # 'views/family_product.xml', # TODO: can be removed after installing yoko_stock
        # # 'views/partner_city.xml',
        # #'views/partner_kaza.xml',
        "views/stock_picking.xml",
        # # 'views/product.xml',
        # # 'views/product_heirarchy.xml', # TODO: can be removed after installing yoko_stock
        # # 'views/product_offer.xml',
        # # 'views/product_pattern.xml', # TODO: can be removed after installing yoko_stock
        # # 'views/product_pricelist.xml',
        # # 'views/product_template.xml',
        # # 'views/product_series.xml', # TODO: can be removed after installing yoko_stock
        # # 'views/product_size.xml', # TODO: can be removed after installing yoko_stock
        "views/purchase_views.xml",
        # # 'views/description.xml',
        # # 'views/res_currency.xml',
        # # 'views/sale_order_reason.xml',
        "views/sale_view.xml",
        # # 'views/sales_menus.xml',
        # # 'views/return_invoice.xml',
        "views/res_partner_driver.xml",
        # "views/email_templates.xml",
        # # 'views/server_actions.xml',
        # # 'views/stock_location.xml',  # TODO: can be removed after installing yoko_stock
        # # 'views/stock_quant.xml',  # TODO: can be removed after installing yoko_stock
        # # 'views/type_product.xml', # TODO: can be removed after installing yoko_stock
        # # 'views/stock_move_line.xml', # TODO: can be removed after installing yoko_stock
        # # 'views/search_template_view_account_report.xml',
        # # 'views/report_invoice.xml',
        "views/vendors.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/deactivate_some_rules.xml",
        # # 'views/invoice_analysis.xml'
    ],
    "assets": {
        "web.assets_backend": [
            "yoko_customization/static/src/css/sales_view_style.css",
            # 'yoko_customization/static/src/js/m2mfilters.js',
        ],
    },
    "installable": True,
    "auto_install": False,
}
