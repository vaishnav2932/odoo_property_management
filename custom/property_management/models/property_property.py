# -*- coding: utf-8 -*-
from odoo import models, fields


class PropertyProperty(models.Model):
    """Model for storing property details like name,address,Address/location,
    Image of Property, Built date,Can be sold,Legal Amount,Rent,State: Rented,
    Draft (add tracking),Description (show in a tab),Owner (partner)
    """
    _name = 'property.property'
    _description = "property model"
    _inherit = 'mail.thread'

    name = fields.Char(string="Name", required=True, tracking=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    country_id = fields.Many2one('res.country')
    state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', country_id)]")
    country_code = fields.Char(related='country_id.code', string='Country Code')
    image_1920 = fields.Image(string="Image")
    built_date = fields.Date(string="Built Date")
    can_be_sold = fields.Boolean(string="Can be Sold")
    legal_amount = fields.Float(string="Legal Amount")
    rent = fields.Float(string="Rent")
    facility_ids = fields.Many2many('property.facility', string="Facilities")
    owner_id = fields.Many2one('res.partner', string="Owner")
    description = fields.Text()
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('rented', 'Rented'), ('leased', 'Leased'),
                   ('sold', 'Sold')], default='draft', tracking=True)
    rent_lease_count = fields.Integer(string="Rent/Lease", compute='_compute_rent_lease_count', default=0)

    def _compute_rent_lease_count(self):
        """to get count in smart btn"""
        for record in self:
            record.rent_lease_count = self.env['property.property.line'].search_count([('properties_id', '=', self.id)])

    def action_get_rent_lease_record(self):
        """to get related record when clicking the smart btn"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rent/Lease',
            'view_mode': 'list,form',
            'res_model': 'property.management',
            'domain': [('properties_ids.properties_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def unlink(self):
        """to delete all rent/lease management records related to a property when deleting the property"""
        for rec in self:
            lines = self.env['property.property.line'].search([('properties_id', '=', rec.id)])
            for line in lines:
                order = line.rent_lease_record_id
                line.unlink()
                if not order.properties_ids:
                    order.unlink()
        return super(PropertyProperty, self).unlink()


