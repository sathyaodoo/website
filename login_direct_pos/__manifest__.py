{
    "name": "Login POS Directly",
    "version": "19.0.1.0.0",
    "category": "Point of Sale",
    "summary": "Fast & Secure Direct POS Login - Skip Backend, Improve Workflow Efficiency",
    "description": """
        POS Direct Login enables seamless and secure direct access to Point of Sale terminals.
        
        Key Benefits:
        • Streamline user authentication - Direct POS shop access without backend navigation
        • Enhanced Security - Restrict operators to POS only, prevent unauthorized backend access
        • Improved Efficiency - Reduce login time and improve cashier workflows
        • Easy Configuration - Simple setup for multi-shop retail environments
        
        Perfect for:
        - Multi-location retail stores
        - Quick Service Restaurants (QSR)
        - Shopping malls and commercial centers
        - Organizations prioritizing POS operator security
        
        Features:
        • One-click POS access for assigned users
        • Role-based shop assignment and permissions
        • Seamless integration with Odoo POS module
        • Compatible with Odoo 19.0+
        • Production-ready and fully tested
        
        Installation: Simply install and configure user-to-shop assignments in Settings.
        Support: Professional support available at https://auraodoo.tech
    """,
    "author": "Aura Odoo Tech",
    "company": "Aura Odoo Tech",
    "maintainer": "Aura Odoo Tech",
    "website": "https://auraodoo.tech",
    "depends": ["web", "website", "portal", "advance_signup_page", "product","website_sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
        "views/product_tabs.xml",
        "views/res_users_views.xml",
        "views/product_template.xml",
        "views/homepage_view.xml",
        "views/product_page_view.xml",
        "views/footer_view.xml",
        "views/contactus_view.xml",
        "views/des_rating_view.xml",
        "views/product_attribute_table_view.xml",
        "views/product_items.xml",
        "views/terms_and_condition.xml",
        "views/product_quantity.xml",
          # 'ECOOOOOOOOOOOOO',
        'views/best_seller_views.xml',
        'views/recently_added_views.xml',
        'views/featured_product_views.xml',
        'views/new_arrival_views.xml',
        'views/testimonial_views.xml',
        'views/faq_views.xml',
        'views/faq_template_view.xml',
        # ECOOOOOOOOOOOOOOOO END
    ],
    "assets": {
        "web.assets_frontend": [
            "login_direct_pos/static/src/js/components/MiniCart/minicart.js",
            "login_direct_pos/static/src/js/components/MiniCart/minicart.xml",
            "login_direct_pos/static/src/js/frontend/website_sale.js",
            "login_direct_pos/static/src/js/frontend/login_popup.js",
            "login_direct_pos/static/src/scss/login_popup.scss",
        ],
    },
    "images": ["static/description/banner.gif"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}
