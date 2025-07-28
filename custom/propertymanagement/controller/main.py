import json
from odoo import http
from odoo.http import request, Controller, route, content_disposition
# from odoo.http import content_disposition, request, route
from odoo.tools import html_escape


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

    @http.route('/get_property_amount', type='json', auth='public', website=True)
    def get_property_amount(self, property_id, **kwargs):
        # Find the latest rent/lease record for the given property
        rent_record = request.env['rental_and_lease.management'].sudo().search([
            ('property_id', '=', int(property_id))
        ], order='id desc', limit=1)

        amount = 0
        if rent_record:
            property_record = rent_record.property_id
            if rent_record.type == 'rental':
                amount = property_record.rent_amount
            elif rent_record.type == 'lease':
                amount = property_record.leagal_amount  # possibly a typo for legal_amount

        return amount


@http.route('/create/rentlease', type="http", auth="public", website=True)
def create_rent_lease_order(self, **post):
    return request.render('property_management.rentlease_success_template', )
