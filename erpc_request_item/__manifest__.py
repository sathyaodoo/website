{
    'name': 'Employee Request For Item',
    'version': '19.0.1.0.0',
    'summary': 'Employee Request For Item',
    'description': """
        Helps you to manage Request Item of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': 'ERP Cloud SARL',
    'website': "https://www.erpcloudllc.com/",
    'depends': ['hr', 'base', 'sale', 'product','stock','sale_order_lot_selection'],
    'data': [
        'security/ir.model.access.csv',
        'views/request_item.xml',
        'views/hr_employee.xml',
        'views/request_item_seq.xml',
    ],
    'license': 'OPL-1',
}
