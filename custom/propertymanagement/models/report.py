from datetime import datetime
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
        ], default='draft', tracking=True
    )
    owner_id = fields.Many2one('res.partner')
    tenant_ids = fields.Many2many('res.partner')
    type = fields.Selection([
        ('rental', 'Rental'),
        ('lease', 'Lease'),
    ], default='rental')

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
        if not conditions:
            raise ValidationError("Fill at least one field.")
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
            WHERE
                {' AND '.join(conditions)}
        """
        self.env.cr.execute(query, tuple(params))
        records = self.env.cr.fetchall()
        print(records)
        if not records:
            raise ValidationError("No records found.")
        today_str = datetime.today().strftime('%d-%m-%Y')
        data = {
            'form_data': {
                'from_date': self.from_date,
                'to_date': self.to_date,
                'state': self.state,
                'type': self.type,
                'today': today_str
            },
            'report_lines': records,
        }
        return self.env.ref('propertymanagement.action_report_rent_lease_order').report_action(
            self, data=data
        )
