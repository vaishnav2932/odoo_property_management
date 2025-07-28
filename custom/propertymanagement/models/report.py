import base64
from datetime import datetime
import json
import io
import xlsxwriter
from odoo.tools import json_default
from odoo import fields, models, api
from odoo.exceptions import ValidationError
from io import BytesIO


class RentLeaseReport(models.TransientModel):
    _name = 'rentlease.report.wizard'
    _description = "Rentlease Wizard"
    property_ids = fields.Many2many('property.management', string="Property")
    from_date = fields.Date()
    to_date = fields.Date()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('inapprove', 'In Approve'),
            ('approved', 'Approved'),
            ('confirmed', 'Confirmed'),
            ('closed', 'Closed'),
            ('returned', 'Returned'),
            ('expired', 'Expired'),
        ],
    )
    owner_id = fields.Many2one('res.partner')
    tenant_ids = fields.Many2many('res.partner')
    type = fields.Selection([
        ('rental', 'Rental'),
        ('lease', 'Lease'),
    ], )
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id',
                                  readonly=False, required=True, store=True, precompute=True)
    currency_symbol = fields.Char(related='currency_id.symbol')

    @api.depends('company_id')
    def _compute_currency_id(self):
        for program in self:
            program.currency_id = program.company_id.currency_id or program.currency_id

    def print_pdf_report(self):
        conditions = []
        params = []
        if self.property_ids:
            conditions.append("property_management.id IN %s")
            params.append(tuple(self.property_ids.ids))
        if self.owner_id:
            conditions.append("res_partner_owner.id = %s")
            params.append(self.owner_id.id)
        if self.tenant_ids:
            conditions.append("res_partner_tenant.id IN %s")
            params.append(tuple(self.tenant_ids.ids))
        if self.type:
            conditions.append("rental_and_lease_management.type = %s")
            params.append(self.type)
        if self.state:
            conditions.append("rental_and_lease_management.state = %s")
            params.append(self.state)
        if self.from_date:
            conditions.append("rental_and_lease_management.start_date >= %s")
            params.append(self.from_date)
        if self.to_date:
            conditions.append("rental_and_lease_management.start_date <= %s")
            params.append(self.to_date)
        query = f"""
            SELECT
                property_management.property_name,
                res_partner_owner.name AS owner_name,
                rental_and_lease_management.sequence,
                res_partner_tenant.name AS tenant_name,
                rental_and_lease_management.state,
                rental_and_lease_management.type,
                rental_and_lease_management.start_date,
                rental_and_lease_management.end_date,
                total_amount
            FROM
                property_line
            INNER JOIN
                property_management ON property_line.property_id = property_management.id
            INNER JOIN
                res_partner AS res_partner_owner ON property_management.owner_id = res_partner_owner.id
            INNER JOIN
                rental_and_lease_management ON property_line.property_rent_lease_id = rental_and_lease_management.id
            INNER JOIN
                res_partner AS res_partner_tenant ON rental_and_lease_management.tenant_id = res_partner_tenant.id
        """
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        self.env.cr.execute(query, tuple(params))
        results = self.env.cr.fetchall()
        records = [{
            'sno': i + 1,
            'property': row[0],
            'owner': row[1],
            'sequence': row[2],
            'tenant': row[3],
            'state': row[4],
            'type': row[5],
            'start_date': row[6],
            'end_date': row[7],
            'amount': row[8],
        } for i, row in enumerate(results)]
        if not records:
            raise ValidationError("No records found.")
        today_str = datetime.today().strftime('%d-%m-%Y')
        property_count = len(self.property_ids)
        tenant_count = len(self.tenant_ids)
        type_column = not bool(self.type)
        state_column = not bool(self.state)
        owner_column = not bool(self.owner_id.complete_name)
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'state': self.state if self.state else None,
            'type': dict(self._fields['type'].selection).get(self.type),
            'property': self.property_ids.property_name if self.property_ids and property_count == 1 else '',
            'tenant': self.tenant_ids.complete_name if self.tenant_ids and tenant_count == 1 else '',
            'owner': self.property_ids.owner_id.complete_name if property_count == 1 else '',
            'owner_name': self.owner_id.complete_name if self.owner_id.complete_name else None,
            'today': today_str,
            'currency_symbol': self.currency_symbol,
            'report_lines': records,
            'property_count': property_count,
            'tenant_count': tenant_count,
            'type_column': type_column,
            'state_column': state_column,
            'owner_column': owner_column,
        }
        return self.env.ref('property_management_erp.action_report_rent_lease_order').report_action(
            self, data=data
        )

    # xlsx report
    def print_xlsx_report(self):
        conditions = []
        params = []
        if self.property_ids:
            conditions.append("property_management.id IN %s")
            params.append(tuple(self.property_ids.ids))
        if self.owner_id:
            conditions.append("res_partner_owner.id = %s")
            params.append(self.owner_id.id)
        if self.tenant_ids:
            conditions.append("res_partner_tenant.id IN %s")
            params.append(tuple(self.tenant_ids.ids))
        if self.type:
            conditions.append("rental_and_lease_management.type = %s")
            params.append(self.type)
        if self.state:
            conditions.append("rental_and_lease_management.state = %s")
            params.append(self.state)
        if self.from_date:
            conditions.append("rental_and_lease_management.start_date >= %s")
            params.append(self.from_date)
        if self.to_date:
            conditions.append("rental_and_lease_management.start_date <= %s")
            params.append(self.to_date)
        query = f"""
                    SELECT
                        property_management.property_name,
                        res_partner_owner.name AS owner_name,
                        rental_and_lease_management.sequence,
                        res_partner_tenant.name AS tenant_name,
                        rental_and_lease_management.state,
                        rental_and_lease_management.type,
                        rental_and_lease_management.start_date,
                        rental_and_lease_management.end_date,
                        total_amount
                    FROM
                        property_line
                    INNER JOIN
                        property_management ON property_line.property_id = property_management.id
                    INNER JOIN
                        res_partner AS res_partner_owner ON property_management.owner_id = res_partner_owner.id
                    INNER JOIN
                        rental_and_lease_management ON property_line.property_rent_lease_id = rental_and_lease_management.id
                    INNER JOIN
                        res_partner AS res_partner_tenant ON rental_and_lease_management.tenant_id = res_partner_tenant.id
                """
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        self.env.cr.execute(query, tuple(params))
        results = self.env.cr.fetchall()
        records = [{
            'sn': i + 1,
            'property': row[0],
            'owner': row[1],
            'sequence': row[2],
            'tenant': row[3],
            'state': row[4],
            'type': row[5],
            'start_date': row[6],
            'end_date': row[7],
            'amount': row[8],
        } for i, row in enumerate(results)]
        if not records:
            raise ValidationError("No records found.")
        today_str = datetime.today().strftime('%d-%m-%Y')
        property_count = len(self.property_ids)
        tenant_count = len(self.tenant_ids)
        type_column = not bool(self.type)
        state_column = not bool(self.state)
        owner_column = not bool(self.owner_id.complete_name)
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'state': self.state if self.state else None,
            'type': dict(self._fields['type'].selection).get(self.type),
            'property': self.property_ids.property_name if self.property_ids and property_count == 1 else '',
            'tenant': self.tenant_ids.complete_name if self.tenant_ids and tenant_count == 1 else '',
            'owner': self.property_ids.owner_id.complete_name if property_count == 1 else '',
            'owner_name': self.owner_id.complete_name if self.owner_id.complete_name else None,
            'today': today_str,
            'currency_symbol': self.currency_symbol,
            'report_lines': records,
            'property_count': property_count,
            'tenant_count': tenant_count,
            'type_column': type_column,
            'state_column': state_column,
            'owner_column': owner_column,
            'company': self.company_id.name,
            # 'logo': self.company_id.logo_web,
            'company_street1': self.company_id.street,
            'company_street2': self.company_id.street2,
            'company_city': self.company_id.city,
            'company_country': self.company_id.country_id.name,
            'company_state': self.company_id.state_id.name,
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'rentlease.report.wizard',
                'options': json.dumps(data,
                                      default=json_default),
                'output_format': 'xlsx',
                'report_name': 'Rent Lease Report',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 14})
        headings = workbook.add_format(
            {'font_size': '11px', 'font_color': '#FFFFFF', 'align': 'center', 'bold': True, 'bg_color': '#000000'})
        txt_format = workbook.add_format({'font_size': 10})
        right_format = workbook.add_format({'align': 'right', 'font_size': 10})
        today = f" Date: {datetime.today().strftime('%d-%m-%Y')}"
        company_name = (data.get('company'))
        street1 = (data.get('company_street1'))
        city = (data.get('company_city'))
        country = (data.get('company_country'))
        state = (data.get('company_state'))
        sheet.set_column('C:C', 5)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 10)
        sheet.set_column('I:I', 10)
        sheet.set_column('J:J', 10)
        sheet.set_column('K:K', 10)
        row = 17
        col = 2
        report_data = data['report_lines']
        currency_symbol = data.get('currency_symbol')
        company = self.env.company
        sheet.merge_range('J8:M1', f"{company_name}\n{street1}\n{city}\n{country}\n{state}")
        if company.logo:
            logo_data = base64.b64decode(company.logo)
            logo_stream = BytesIO(logo_data)
            sheet.insert_image('J1', 'logo.png', {'image_data': logo_stream, 'x_scale': 0.3, 'y_scale': 0.3})
            property_name = data.get('property')
            owner_name = data.get('owner')
            tenant_name = data.get('tenant')
        if data.get('property_count') == 1:
            sheet.set_column('E:E', 10)
            sheet.merge_range('E14:G13', f"Property : {property_name}\nOwner : {owner_name}")
            sheet.merge_range('E16:F16', today)
            sheet.merge_range('G10:I9', 'Rent/Lease XLSX Report', head)
        else:
            sheet.merge_range('C16:D16', today)
            sheet.merge_range('F10:H9', 'Rent/Lease XLSX Report', head)
        if data.get('tenant_count') == 1:
            sheet.merge_range('C14:E14', f"Tenant : {tenant_name}")
        row_num = 18
        for rec in report_data:
            amount = rec['amount']
            amount_symbol = f"{currency_symbol}{amount}"
            type_selection = dict(self._fields['type']._description_selection(self.env)).get(rec['type'])
            state_selection = dict(self._fields['state']._description_selection(self.env)).get(rec['state'])
            if data.get('property_count') == 1:
                sheet.write(row, col + 2, 'SN', headings)
                sheet.write(row_num, 4, rec['sn'], txt_format)
                sheet.write(row, col + 3, 'Sequence', headings)
                sheet.write(row_num, 5, rec['sequence'], right_format)
            else:
                sheet.write(row, col + 0, 'SN', headings)
                sheet.write(row_num, 2, rec['sn'], txt_format)
                sheet.write(row, col + 1, 'Sequence', headings)
                sheet.write(row_num, 3, rec['sequence'], right_format)
            if data.get('property_count') != 1:
                sheet.write(row, col + 2, 'Property', headings)
                sheet.write(row_num, 4, rec['property'], txt_format)
                sheet.write(row, col + 3, 'Owner', headings)
                sheet.write(row_num, 5, rec['owner'], txt_format)
            sheet.write(row, col + 4, 'Type', headings)
            sheet.write(row_num, 6, type_selection, txt_format)
            if data.get('tenant_count') != 1:
                sheet.write(row, col + 5, 'Tenant', headings)
                sheet.write(row_num, 7, rec['tenant'], txt_format)
                sheet.write(row, col + 6, 'Start', headings)
                sheet.write(row_num, 8, rec['start_date'], right_format)
                sheet.write(row, col + 7, 'End', headings)
                sheet.write(row_num, 9, rec['end_date'], right_format)
                sheet.write(row, col + 8, 'Amount', headings)
                sheet.write(row_num, 10, amount_symbol, right_format)
                sheet.write(row, col + 9, 'State', headings)
                sheet.write(row_num, 11, state_selection, txt_format)
            else:
                sheet.write(row, col + 5, 'Start', headings)
                sheet.write(row_num, 7, rec['start_date'], right_format)
                sheet.write(row, col + 6, 'End', headings)
                sheet.write(row_num, 8, rec['end_date'], right_format)
                sheet.write(row, col + 7, 'Amount', headings)
                sheet.write(row_num, 9, amount_symbol, right_format)
                sheet.write(row, col + 8, 'State', headings)
                sheet.write(row_num, 10, state_selection, txt_format)
            row_num += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
