# -*- coding: utf-8 -*-
{
    'name': 'HR Absentees List Report',
    'version': '13.0.1.0.0',
    'author': 'Sneha Rose',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'category': 'Attendance',
    'summary': 'For managing employees of an organization',
    'description': """
Organization and management of employees.
======================================


Key Features
------------
* Manage your sales

""",
    'depends': ['base', 'hr', 'hr_holidays', 'hr_attendance', 'odoo_report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'report/report_template_tem.xml',
        'report/report.xml',
        'wizards/reportxml.xml',
        'views/Employee_abs_view.xml',
        'views/template.xml',
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'qweb': [],

}
