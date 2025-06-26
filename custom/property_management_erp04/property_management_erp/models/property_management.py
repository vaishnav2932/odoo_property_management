# encoding utf-8
from odoo import fields, models, api


class Property(models.Model):
    _name = "property.management"
    _description = "property management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "property_name"

    property_name = fields.Char(required=True)
    property_image = fields.Image()
    street1 = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    country_id = fields.Many2one('res.country')
    state_id = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=?', country_id)]")
    can_be_sold = fields.Boolean()
    legal_amount = fields.Float()
    rent = fields.Float(readonly=False, store=True)
    description = fields.Text()
    owner_id = fields.Many2one('res.partner')
    built_date = fields.Date()
    facility_ids = fields.Many2many('property.facilities', string="Facilities")
    rent_or_lease_id = fields.Many2one('property.line')
    property_type_id = fields.Many2one('rental_and_lease.management')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('rented', 'Rented'),
            ('leased', 'Leased'),
            ('sold', 'Sold')
        ], tracking=True, default='draft'
    )

    def action_get_rent_and_lease(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rent/lease',
            'view_mode': 'list,form',
            'res_model': 'property.line',
            'domain': [('property_id', '=', self.id)],
            'context': "{'create': True}"
        }



class Facilities(models.Model):
    _name = "property.facilities"
    _description = "Property facilities"
    _rec_name = "facility"

    facility = fields.Char(required=True)
