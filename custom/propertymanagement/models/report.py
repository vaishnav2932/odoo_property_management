from odoo import fields, models


class WhatsappSendMessage(models.TransientModel):
    """This model is used for sending WhatsApp messages through Odoo."""
    _name = 'rentlease.report.wizard'
    _description = "Rentlease Wizard"
    property_id = fields.Many2one('property.management', string="Property")
    from_date = fields.Date()
    to_date = fields.Date()

    def print_pdf_report(self):
        data = {
            'property_name': self.property_id,
            'from_date': self.from_date.strftime('%Y-%m-%d'),
            'to_date': self.to_date.strftime('%Y-%m-%d'),
        }
        return self.env.ref('propertymanagement.action_report_rent_lease_order').report_action(self,
                                                                                               data={'data': data})
