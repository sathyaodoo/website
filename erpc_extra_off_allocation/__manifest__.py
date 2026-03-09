{
    "name": "Extra Off Hours",
    "summary": "Extra Off Hours",
    "description": """Extra Off Hours""",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    'author': 'ERP Cloud SARL',
    'website': "https://www.erpcloudllc.com/",
    "depends": [
        "erpc_daily_attendance", "hr_holidays", "erpc_contracts_fields_positions",
    ],
    "data": [
        "data/hr_work_entry_type.xml",
        # "data/scheduled_action.xml",
        # # "views/hr_employee.xml", TODO: To keep it commented
        # "views/hr_leave_allocation_views.xml",
    ],
}
