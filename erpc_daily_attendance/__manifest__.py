{
    "name": "Daily Attendance",
    "summary": "Daily Attendance",
    "description": """Daily Attendance""",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    'author': 'ERP Cloud SARL',
    'website': "https://www.erpcloudllc.com/",
    "depends": [
        "base",
        "hr_payroll",
        "hr_attendance",
        # "hr_work_entry_contract",
        # 'hr_holidays_attendance',
        # 'hr_work_entry_holidays'
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/hr_work_entry_type.xml',
        # 'data/actions.xml',
        # "views/daily_attendance.xml",
    ],
}
