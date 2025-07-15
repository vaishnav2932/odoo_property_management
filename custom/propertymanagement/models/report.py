from odoo import fields, models
from odoo.exceptions import ValidationError


class WhatsappSendMessage(models.TransientModel):
    """This model is used for sending WhatsApp messages through Odoo."""
    _name = 'rentlease.report.wizard'
    _description = "Rentlease Wizard"
    property_id = fields.Many2one('property.management', string="Property")
    from_date = fields.Date()
    to_date = fields.Date()

    def print_pdf_report(self):
        if not self.property_id:
            raise ValidationError("Please select a property to generate the report.")

        query = """
            SELECT
                property_management.property_name,
                res_partner_owner.name AS owner_name,
                rental_and_lease_management.sequence,
                res_partner_tenant.name AS tenant_name,
                rental_and_lease_management.state,
                rental_and_lease_management.type
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
                property_management.id = %s
        """
        self.env.cr.execute(query, (self.property_id.id,))
        report = self.env.cr.fetchall()

        if not report:
            raise ValidationError("No records found for the selected property.")

        data = {
            'form_data': {
                'property_name': self.property_id.property_name,
            },
            'report_lines': report,
        }

        return self.env.ref('propertymanagement.action_report_rent_lease_order').report_action(self,
                                                                                                    data={'data': data})

#
#
#     def print_pdf_report(self):
#         if not self.property_id:
#             raise ValidationError("Please select a property to generate the report.")
#
#         query = """
#             SELECT
#                 property_management.property_name,
#                 res_partner_owner.name AS owner_name,
#                 rental_and_lease_management.sequence,
#                 res_partner_tenant.name AS tenant_name,
#                 rental_and_lease_management.state,
#                 rental_and_lease_management.type
#             FROM
#                 property_line
#             INNER JOIN
#                 property_management ON property_line.property_id = property_management.id
#             INNER JOIN
#                 res_partner AS res_partner_owner ON property_management.owner_id = res_partner_owner.id
#             INNER JOIN
#                 rental_and_lease_management ON property_line.property_rent_lease_id = rental_and_lease_management.id
#             INNER JOIN
#                 res_partner AS res_partner_tenant ON rental_and_lease_management.tenant_id = res_partner_tenant.id
#             WHERE
#                 property_management.id = %s
#         """
#
#         self.env.cr.execute(query, (self.property_id.id,))
#         report = self.env.cr.fetchall()
#
#         if not report:
#             raise ValidationError("No records found for the selected property.")
#
#         data = {
#             'form_data': {
#                 'property_name': self.property_id.property_name,
#             },
#             'report_lines': report,
#         }
#
#         return self.env.ref('propertymanagement.action_report_rent_lease_order').report_action(self,
#                                                                                                     data={'data': data})

