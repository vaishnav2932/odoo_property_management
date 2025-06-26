# encoding utf-8
from odoo import fields, models, api, _


class PropertyLine(models.Model):
    _name = "property.line"
    _description = "Property Line"
    _rec_name = "property_id"

    property_id = fields.Many2one("property.management", string="Property name", ondelete='cascade')
    sequence = fields.Char(related="property_rent_lease_id.sequence")
    total_amount = fields.Float(compute="_compute_total_amount")
    property_rent_lease_id = fields.Many2one("rental_and_lease.management", ondelete='cascade')
    amount = fields.Float(compute="_compute_amount", readonly=False, inverse="_inverse_amount", )
    total_days = fields.Integer(related="property_rent_lease_id.total_days")
    original_rent_amount = fields.Float(related='property_id.rent')
    original_legal_amount = fields.Float(related='property_id.legal_amount')

    @api.depends('amount', 'total_days')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.amount * record.total_days

    @api.depends('property_rent_lease_id.type', 'property_id.rent', 'property_id.legal_amount')
    def _compute_amount(self):
        for record in self:
            if record.property_rent_lease_id.type == 'rental':
                record.amount = record.property_id.rent or 0.0
            elif record.property_rent_lease_id.type == 'lease':
                record.amount = record.property_id.legal_amount or 0.0
            else:
                record.amount = 0.0

    def _inverse_amount(self):
        for record in self:
            if record.property_rent_lease_id.type == 'rental':
                record.property_id.rent = record.amount
            elif record.property_rent_lease_id.type == 'lease':
                record.property_id.legal_amount = record.amount
