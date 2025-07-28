# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PropertyWizard(models.TransientModel):
    """this model is for property management pdf report"""
    _name = 'property.wizard'
    _description = 'Property PDF Wizard'

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('toapprove', 'To Approve'), ('confirmed', 'Confirmed'), ('closed', 'Closed'),
                   ('returned', 'Returned'), ('expired', 'Expired')])
    tenant_id = fields.Many2one('res.partner', string="Tenant")
    owner_id = fields.Many2one('res.partner')
    property_type = fields.Selection(selection=[('rent', 'Rent'), ('lease', 'Lease')])
    property_id = fields.Many2one('property.property', string="Property")

    def action_pdf(self):
        """if user click pdf btn then, pdf report will be generated with given filter"""
        print("accepted")


        # query = """ select t.name as tenant, o.name as owner, ppl.properties_id as property_id,
        # ppl.rent_lease_amount as rent_lease_amount, pm.start_date, pm.end_date,
        # pm.state, pm.property_type from
        # property_management as pm join property_property pp on pm.property_id = pp.id join
        # property_property_line ppl on ppl.properties_id = pp.id join res_partner t
        # on pm.tenant_id = t.id join res_partner o on o.id = pp.owner_id join property
        # where
        #    ppl.property_id = %s and pm.property_type = '%s' and pm.tenant_id = %s and pm.state = '%s'
        #    and pm.start_date = '%s' and pm.end_date = '%s'
        #
        # """ % (self.property_id.id, self.property_type, self.tenant_id.id, self.state, self.from_date, self.to_date)

        query = """ select t.name as tenant, pm.property_type from
                property_management as pm  join res_partner t
                on pm.tenant_id = t.id
                where pm.property_type = '%s' and pm.tenant_id = %s""" % (self.property_type , self.tenant_id.id)
        self.env.cr.execute(query)
        report = self.env.cr.dictfetchall()
        data = {'date': self.read()[0], 'report': report}
        return self.env.ref('property_management.action_report_property_rent_form').report_action(None, data=data)


    @api.constrains(from_date, to_date)
    def _check_from_date(self):
        for rec in self:
            if rec.from_date > rec.to_date:
                raise ValidationError("From date cannot be greater than To date")


