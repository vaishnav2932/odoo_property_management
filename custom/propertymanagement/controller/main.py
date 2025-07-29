import json
from dataclasses import fields

from odoo import http,fields
from odoo.http import content_disposition, request
from odoo.tools import html_escape
from odoo.http import request, Controller, route

class XLSXReportController(http.Controller):
    @http.route('/xlsx_reports', type='http', auth='user',
                csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name,
                        token='ads'):
        """ Return data to python file passed from the javascript"""
        session_unique_id = request.session.uid
        report_object = request.env[model].with_user(session_unique_id)
        options = json.loads(options)
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[('Content-Type', 'application/vnd.ms-excel'), (
                        'Content-Disposition',
                        content_disposition(f"{report_name}.xlsx"))
                             ]
                )
                report_object.get_xlsx_report(options, response)
                response.set_cookie('fileToken', token)
                return response
        except Exception:
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
            }
            return request.make_response(html_escape(json.dumps(error)))


class PropertyManagementController(http.Controller):
    @http.route('/rentlease', type="http", auth="public", website=True)
    def rent_lease_orders(self, **kwargs):
        properties = request.env['property.management'].sudo().search([])
        # rentlease = request.env['rental_and_lease.management'].sudo().search([])
        type_selection_options = request.env['rental_and_lease.management'].sudo()._fields['type'].selection

        tenant = request.env.user.name
        datas = {
            'properties': properties,
            'tenant_id': tenant,
            'type_options': type_selection_options,
        }
        return request.render('propertymanagement.rentlease_form_template', datas)

    @http.route('/form/submit', type='http', auth='public', website=True, methods=['POST'])
    def form_submit(self, **kwargs):

        property_ids = request.httprequest.form.getlist('property_id[]')
        total_amounts = request.httprequest.form.getlist('total_amount[]')

        prop_line = []
        for prop_id, amount in zip(property_ids, total_amounts):
            if prop_id and amount:
                prop_line.append(fields.Command.create({
                    'property_id': int(prop_id),
                    'total_amount': float(amount),
                }))

        request.env['rental_and_lease.management'].sudo().create({
            'tenant_id': request.env.user.id,
            'type': kwargs.get('type'),
            'start_date': kwargs.get('start_date'),
            'end_date': kwargs.get('end_date'),
            'property_ids': prop_line
        })

        return request.redirect('/')






