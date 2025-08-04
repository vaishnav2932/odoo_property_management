import base64
import json
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, fields
from odoo.tools import html_escape
from odoo.http import request, content_disposition


class XLSXReportController(http.Controller):
    @http.route('/xlsx_reports', type='http', auth='user',
                csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name,
                        token='ads'):
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


class CustomPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # if 'portal_rent_lease' in counters:
        values['rent_lease_counts'] = request.env['property.line'].sudo().search_count([])
        return values

    @http.route('/rentalandlease', type='http', auth="public", website=True)
    def portalRentLeaseList(self, **kwargs):
        print("controller working")
        rentlease_obj = request.env['rental_and_lease.management']
        rentlease = rentlease_obj.search([('tenant_id', '=', request.env.user.id)])
        values = {'rentlease': rentlease, 'page_name': 'rentalandlease'}
        return request.render('propertymanagement.portal_my_home_rentlease_views', values)

    @http.route('/rentalandlease/<model(rental_and_lease.management):rent>/', type='http', website=True)
    def portalRentLeaseForm(self, rent, **kwargs):
        values = {'rentlease': rent, 'page_name': 'rentalandlease_form'}
        return request.render('propertymanagement.portal_my_home_rentlease_form_views', values)


class PropertySnippetController(http.Controller):
    @http.route('/get_properties', auth="public", type='json',
                website=True)
    def get_property(self):
        """Get the website categories for the snippet."""
        properties = request.env[
            'property.management'].sudo().search_read(
            [], fields=['property_name', 'property_image']
        )
        values = {
            'properties': properties,
        }
        return values


class PropertyDetailController(http.Controller):
    @http.route('/get_properties/<model(property.management):properties>/', auth="public", type="http", website=True)
    def get_property_details(self, properties, **kwargs):
        image_data = ''
        if properties.property_image:
            image_data = base64.b64encode(properties.property_image).decode('utf-8')
        values = {'properties': properties, 'image_data':image_data, 'page_name': 'property_details'}
        return request.render('propertymanagement.property_details_view', values)
