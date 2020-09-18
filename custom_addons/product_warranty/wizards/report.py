from collections import Counter

from odoo import models, fields, api


class AttendanceRecapReportWizard(models.TransientModel):
    _name = 'attendance.recap.report.wizard'

    date_start = fields.Date(string="Start Date", default=fields.Date.today)
    date_end = fields.Date(string="End Date")
    type = fields.Selection([('date_wise', 'Date Wise'), ('employee_wise', 'Employee Wise')],
                            required=True)

    def get_report(self):
        view_type = dict(self._fields['type'].selection).get(self.type)
        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'view_mode': view_type
        }
        if view_type == 'Date Wise':
            return self.env.ref('hr_absentees_report.absentees_list_report').report_action(self, data=data)

        return self.env.ref('hr_absentees_report.absentees_list_report_emp').report_action(self, data=data)

    def view_report_excel(self):
        view_type = dict(self._fields['type'].selection).get(self.type)

        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'view_mode': view_type

        }

        return self.env.ref('hr_absentees_report.hr_absentees_report_excel').report_action(self, data=data)


class ReportAttendanceRecap(models.AbstractModel):
    _name = 'report.hr_absentees_report.report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['date_start']
        date_end = data['date_end']
        view_mode = data['view_mode']

        if data['date_start'] and data['date_end']:
            self._cr.execute(
                """ select id as docs from
               employee_absent_list
                where to_date >= %s and to_date <= %s """,
                (date_start, date_end,))

        elif data['date_end']:
            self._cr.execute(
                """ select id as docs from
               employee_absent_list
                where to_date <= %s """,
                [date_end])
        elif date_start:
            self._cr.execute(
                """ select id as docs from
               employee_absent_list
                where to_date = %s""", [date_start])
        else:
            self._cr.execute(
                """ select id as docs from
               employee_absent_list
                """)
        records = []
        record = self._cr.dictfetchall()
        doc_id = [y['docs'] for y in record]
        for docc in doc_id:
            record = self.env['employee.absent.list'].browse(docc)
            records.append(record)
        count = 0
        return {
            'date_start': date_start,
            'date_end': date_end,
            'view_type': view_mode,
            'docs': records
        }


class ReportAttendanceRecapSecond(models.AbstractModel):
    _name = 'report.hr_absentees_report.report_template_emp'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['date_start']
        date_end = data['date_end']
        view_mode = data['view_mode']

        if data['date_start'] and data['date_end']:
            self._cr.execute(
                """ select id as docs from
               employee_absent_list
                where to_date >= %s and to_date <= %s """,
                (date_start, date_end,))

        elif data['date_end']:
            self._cr.execute(
                """ select id as docs group by id from
               employee_absent_list
                where to_date <= %s """,
                [date_end])

        elif date_start:
            self._cr.execute(
                """ SELECT  id as docs FROM
               employee_absent_list 
                where to_date = %s """, [date_start])
        else:
            self._cr.execute(
                """ select id as docs from
               employee_absent_list
                """)
        records = []
        record = self._cr.dictfetchall()
        doc_id = [y['docs'] for y in record]
        for docc in doc_id:
            record = self.env['employee.absent.list'].browse(docc)
            records.append(record)

        mylist = []
        validated = {}
        refused = {}
        for rec in records:
            mylist.append(rec.idd.id)
        c = Counter(mylist)
        records.clear()
        for doc in c.keys():
            validated_count = 0
            refused_count = 0

            record = self.env['hr.employee'].search([('id', '=', doc)])
            records.append(record)
            list = self.env['hr.leave'].search(
                [('employee_id', '=', doc), ('state', '=', 'validate1') or ('state', '=', 'validate')])
            for j in list:
                validated_count += 1
            validated[doc] = validated_count
            list_list = self.env['hr.leave'].search([('employee_id', '=', doc), ('state', '=', 'refused')])
            for j in list_list:
                refused_count += 1
            refused[doc] = refused_count

        return {
            'date_start': date_start,
            'date_end': date_end,
            'view_type': view_mode,
            'docs': records,
            'ab_count': c,
            'count': validated,
            'refuse': refused

        }


class AbsenteesReportExcel(models.AbstractModel):
    _name = 'report.hr_absentees_report.report_template_xls'
    _inherit = 'report.odoo_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data=None, line=None):
        date_start = data['date_start']
        date_end = data['date_end']

        sheet = workbook.add_worksheet()
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        sub_head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '10px'})
        date = workbook.add_format({'font_size': '10px', 'align': 'center', 'num_format': 'yyyy-m-d'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})

        sheet.merge_range('B2:Q3', 'HR Absentees XLSX Report', head)
        sheet.write('B5', 'From:', sub_head)
        sheet.merge_range('C5:D5', data['date_start'], date)
        sheet.write('F5', 'To:', sub_head)
        sheet.merge_range('G5:H5', data['date_end'], date)
        sheet.merge_range('C6:C7', 'Sl No', sub_head)
        sheet.merge_range('D6:E7', 'Employee Name', sub_head)
        sheet.merge_range('F6:G7', 'Employee ID', sub_head)
        sheet.merge_range('H6:I7', 'Taken Leaves', sub_head)
        sheet.merge_range('J6:K7', 'Approved', sub_head)
        sheet.merge_range('L6:M7', 'Refused', sub_head)

        if data['date_start'] and data['date_end']:
            self._cr.execute(
                """ select id as docs from
               employee_absent_list
                where to_date >= %s and to_date <= %s """,
                (date_start, date_end,))

        elif data['date_end']:
            self._cr.execute(
                """ select id as docs group by id from
               employee_absent_list
                where to_date <= %s """,
                [date_end])

        elif date_start:
            self._cr.execute(
                """ SELECT  id as docs FROM
               employee_absent_list 
                where to_date = %s """, [date_start])
        else:
            self._cr.execute(
                """ select id as docs from
               employee_absent_list
                """)
        records = []
        record = self._cr.dictfetchall()
        doc_id = [y['docs'] for y in record]
        for docc in doc_id:
            record = self.env['employee.absent.list'].browse(docc)
            records.append(record)

        mylist = []
        validated = {}
        refused = {}
        for rec in records:
            mylist.append(rec.idd.id)
        c = Counter(mylist)
        records.clear()
        for doc in c.keys():
            validated_count = 0
            refused_count = 0

            record = self.env['hr.employee'].search([('id', '=', doc)])
            records.append(record)
            list = self.env['hr.leave'].search(
                [('employee_id', '=', doc), ('state', '=', 'validate1') or ('state', '=', 'validate')])
            for j in list:
                validated_count += 1
            validated[doc] = validated_count
            list_list = self.env['hr.leave'].search([('employee_id', '=', doc), ('state', '=', 'refused')])
            for j in list_list:
                refused_count += 1
            refused[doc] = refused_count
        col_num = 2
        j = 9
        i = 1
        if record:
            for item in records:
                print(i)
                sheet.write(j, col_num, i, txt)
                sheet.write('C' + str(j), i, txt)
                sheet.merge_range('D' + str(j) + ':' + 'E' + str(j), item.name, txt)
                sheet.merge_range('F' + str(j) + ':' + 'G' + str(j), item.id, txt)
                sheet.merge_range('H' + str(j) + ':' + 'I' + str(j), c[item.id], txt)
                sheet.merge_range('J' + str(j) + ':' + 'K' + str(j), validated[item.id], txt)
                sheet.merge_range('L' + str(j) + ':' + 'M' + str(j), refused[item.id], txt)
                i += 1
                j += 1
