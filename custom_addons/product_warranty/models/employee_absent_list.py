from datetime import date, datetime, time
from odoo import models, fields, api


class ResConfi(models.TransientModel):
    _inherit = 'res.config.settings'

    com_check = fields.Datetime()

    def set_values(self):
        super(ResConfi, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("com_check", self.com_check)

    def get_values(self):
        res = {}
        params = self.env['ir.config_parameter'].sudo()
        get_order = params.get_param('com_check')
        res.update(com_check=get_order)
        return res


class MyClass(models.Model):
    _name = 'employee.absent.list'
    _rec_name = 'emp_name'

    idd = fields.Many2one('hr.employee', string="id")
    emp_name = fields.Char(String="Employee Name")
    reason = fields.Char(String="Reason")
    status = fields.Char(String="Leave Status")
    approve_by = fields.Char(String="Approved By")
    to_date = fields.Date(String="Date")
    type_of_lve = fields.Char(String="Type Of Leave")
    half = fields.Boolean(default=False)
    count = fields.Integer()
    refused = fields.Integer()
    validated_count = fields.Integer()


class EmployeeList(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def employee_absentees(self):

        today_absentees = self.env['ir.config_parameter'].get_param("com_check")
        who_active = self.env['hr.employee'].search([('active', '=', 'TRUE')])

        final = []  # ABSENTEES LIST
        for employee in who_active:
            if employee.last_check_in:
                if not str(employee.last_check_in) >= today_absentees:
                    final.append(employee)
            else:
                final.append(employee)
        self.env['employee.absent.list'].search([('to_date', '=', date.today())]).unlink()
        print(final)

        for i in final:  # CREATE EMPLOYEE LIST

            self.env['employee.absent.list'].create({
                'idd': i.id,
                'emp_name': i.name,
                'reason': False,
                'status': "Leave not Requested",
                'approve_by': False,
                'type_of_lve': False,
                'to_date': date.today(),
                'half': False,
                'count': False,
                'refused': False,
                'validated_count': False
            })
            print("in final", i.name)

            emp_in_leave = self.env['hr.leave'].search([('employee_id.id', '=', i.id)])  # COMPARE ABSENT EMPLOYEE
            # WITH LEAVE TABLE

            for p in emp_in_leave:  # WRITE IF EMPLOYEE IS IN LEAVE TABLE
                if p.request_date_from == date.today() or p.request_date_from <= date.today() <= p.request_date_to:
                    half = False
                    if p.request_unit_half:
                        half = True
                    self.env['employee.absent.list'].search([('idd', '=', i.id)]).write({
                        'reason': p.name,
                        'status': p.state,
                        'approve_by': p.first_approver_id.name,
                        'type_of_lve': p.holiday_status_id.name,
                        'half': half,
                    })
