# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PropertyPropertyLine(models.Model):
    """for the property line in rent/lease management (one2many field)"""
    _name = 'property.property.line'
    _description = 'Property line'

    properties_id = fields.Many2one('property.property', string="Property")
    rent_lease_record_id = fields.Many2one('property.management', string="rent or lease record")
    rent_lease_amount = fields.Float('Rent/Lease Amount', compute="_compute_rent_lease_amount",
                                     inverse="_inverse_rent_lease_amount")
    total_days = fields.Integer(string="Total days", related="rent_lease_record_id.total_days")
    invoice_line_ids = fields.Many2many('account.move.line')
    total_amount = fields.Float(string="Total amount", compute="_compute_total_amount", store=True, )

    @api.depends("rent_lease_record_id.property_type", "properties_id.rent", "properties_id.legal_amount")
    def _compute_rent_lease_amount(self):
        """to find rent/lese amount when changing property or property type"""
        for rec in self:
            if rec.rent_lease_record_id.property_type == "rent":
                rec.rent_lease_amount = rec.properties_id.rent
            else:
                rec.rent_lease_amount = rec.properties_id.legal_amount

    def _inverse_rent_lease_amount(self):
        """to Add the updated price from rent/lease records(property order line) to the related
        property as a default amount"""
        for rec in self:
            if rec.rent_lease_record_id.property_type == "rent":
                rec.properties_id.rent = rec.rent_lease_amount
            else:
                rec.properties_id.legal_amount = rec.rent_lease_amount

    @api.depends("total_days", "rent_lease_amount")
    def _compute_total_amount(self):
        """to calculate total amount from total days and rent/lease amount"""
        for rec in self:
            if rec.rent_lease_amount:
                rec.total_amount = rec.total_days * rec.rent_lease_amount
