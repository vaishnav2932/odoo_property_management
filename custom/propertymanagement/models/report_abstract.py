from odoo import models, fields
from datetime import datetime


class ReportRentLease(models.AbstractModel):
    _name = 'report.propertymanagement.report_rent_lease_pdf'
    _description = 'Rent Lease PDF Report'

    def _get_report_values(self, docids, data=None):
        today_str = datetime.today().strftime('%d-%m-%Y')  # e.g., 14-07-2025

        return {
            'doc_ids': docids,
            'doc_model': 'rentlease.report.wizard',
            'data': data.get('data') if data else {},
            'today': today_str,
            # Add today's date here
        }
