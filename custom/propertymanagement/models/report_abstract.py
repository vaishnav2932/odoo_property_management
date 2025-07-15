from odoo import models


class ReportRentLease(models.AbstractModel):
    _name = 'report.propertymanagement.report_rent_lease_pdf'
    _description = 'Rent Lease PDF Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['rentlease.report.wizard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'rentlease.report.wizard',
            'docs': docs,
            'data': data,
        }

