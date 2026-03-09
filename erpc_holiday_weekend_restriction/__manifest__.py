{
    "name": "ERPC Holiday Weekend Restriction",
    "category": "HR",
    "author": "ERP Cloud S.A.R.L",
    "sequence": -100,
    "version": "19.0.1.0.0",
    "summary": "Holiday Weekend Restriction",
    "description": """If Friday and Saturday are off in the schedule and the employee takes leave that includes
     Friday and Saturday in the middle, those days will be deducted from the Annual Leave balance. 
     But if the leave is in the beginning or the end it will not be deducted.""",
    "depends": ["base", "hr", "hr_holidays"],
    "data": [
        # "views/view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
