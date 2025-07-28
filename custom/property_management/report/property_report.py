# -*- coding: utf-8 -*-

from odoo import models, api
class PropertyReport(models.AbstractModel):
    _name = 'report.property_management.property_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        # docs = self.env['property.wizard'].browse(docids[1])
        print("ab model")
        print(data['report'][0])
        return {
            'doc_ids': docids,
            'doc_model': 'property.wizard',
            # 'docs': docs,
            'docs': data['report'][0],
            'data': data,
        }
