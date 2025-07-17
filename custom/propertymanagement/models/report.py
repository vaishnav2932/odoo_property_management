from datetime import datetime
import json
import io
import xlsxwriter
from odoo.tools import json_default
from odoo import fields, models
from odoo.exceptions import ValidationError


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
        print(records)
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
            'type': self.type if self.type else None,
            'property': self.property_ids.property_name if self.property_ids and property_count == 1 else '',
            'tenant': self.tenant_ids.complete_name if self.tenant_ids and tenant_count == 1 else '',
            'owner': self.property_ids.owner_id.complete_name if property_count == 1 else '',
            'owner_name': self.owner_id.complete_name if self.owner_id.complete_name else None,
            'today': today_str,
            'report_lines': records,
            'property_count': property_count,
            'tenant_count': tenant_count,
            'type_column': type_column,
            'state_column': state_column,
            'owner_column': owner_column,

        }

        return self.env.ref('propertymanagement.action_report_rent_lease_order').report_action(
            self, data=data
        )

    def print_xlsx_report(self):
        data = {
            'from_date': self.from_date.strftime('%d-%m-%Y') if self.from_date else '',
            'to_date': self.to_date.strftime('%d-%m-%Y') if self.to_date else '',
            'state': self.state,
            'type': self.type,
            'properties': [prop.property_name for prop in self.property_ids],
            'tenants': [tenant.name for tenant in self.tenant_ids],
            'owner': self.owner_id.name if self.owner_id else '',
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'rentlease.report.wizard',
                'options': json.dumps(data),
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
        label_format = workbook.add_format({'bold': True})
        txt_format = workbook.add_format({'font_size': 10})

        # Title
        sheet.merge_range('B2:E2', 'Rent/Lease XLSX Report', head)

        # Filters Info
        sheet.write('A4', 'From Date:', label_format)
        sheet.write('B4', data.get('from_date', ''))
        sheet.write('A5', 'To Date:', label_format)
        sheet.write('B5', data.get('to_date', ''))
        sheet.write('A6', 'Type:', label_format)
        sheet.write('B6', data.get('type', ''))
        sheet.write('A7', 'State:', label_format)
        sheet.write('B7', data.get('state', ''))
        sheet.write('A8', 'Owner:', label_format)
        sheet.write('B8', data.get('owner', ''))

        # Property List
        sheet.write('A10', 'Properties:', label_format)
        row = 10
        for prop in data.get('properties', []):
            sheet.write(row, 1, prop, txt_format)
            row += 1

        # Tenant List
        sheet.write(row + 1, 0, 'Tenants:', label_format)
        row += 2
        for tenant in data.get('tenants', []):
            sheet.write(row, 1, tenant, txt_format)
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
