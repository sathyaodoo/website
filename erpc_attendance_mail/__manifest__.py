{
    "name": "Attendance Mail",
    'author': 'ERP Cloud SARL',
    'website': "https://www.erpcloudllc.com/",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Attendances",
    "summary": "Attendance Per Day",
    "description": """Apply custom calculations on attendance to compute the accepted work hours, overtime, and undertime for an employee.""",
    "depends": ["base", 'hr', 'hr_attendance', 'mail', 'hr_holidays', 'erpc_attendance_machine'],
    "data": [
        # 'security/ir.model.access.csv',
        # 'data/scheduled_action.xml',
        # 'data/ir_actions_server.xml',
        # 'views/attendance.xml',
        # 'views/hr_employee.xml',
    ],
}
