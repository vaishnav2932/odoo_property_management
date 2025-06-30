# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.addons.test_convert.tests.test_env import record


class PropertyLine(models.Model):
    _name = "property.line"
    _description = "Property Line"
    _rec_name = "property_id"

    property_id = fields.Many2one("property.management", string="Property name")
    sequence = fields.Char(related="property_rent_lease_id.sequence")
    total_amount = fields.Float(compute="_compute_total_amount")
    property_rent_lease_id = fields.Many2one("rental_and_lease.management")
    amount = fields.Float(compute="_compute_amount", readonly=False, inverse="_inverse_amount", store=False)
    total_days = fields.Integer(related="property_rent_lease_id.total_days", inverse="_inverse_total_days")
    original_rent_amount = fields.Float(related='property_id.rent')
    original_legal_amount = fields.Float(related='property_id.legal_amount')
    account_move_id = fields.Many2many('account.move')
    invoice_line_ids = fields.One2many('account.move.line', 'property_line_id')
    quantity_invoiced = fields.Float(compute="_compute_quantity_invoiced",
                                     store=False,
                                     )
    quantity_to_invoice = fields.Float(compute='_compute_quantity_to_invoice', )

    @api.depends(
        'invoice_line_ids',
        'invoice_line_ids.quantity',
        'invoice_line_ids.move_id.state',
        'invoice_line_ids.move_id.date',
    )
    def _compute_quantity_invoiced(self):
        for record in self:
            # valid_lines = record.invoice_line_ids.filtered_domain([('move_id.state', '=', 'posted')])
            valid_lines = record.invoice_line_ids.filtered(
                lambda l: l.move_id and l.move_id.state == 'posted'
            )
            latest_line = valid_lines.sorted(lambda l: l.move_id.date or fields.Date.today(), reverse=True)[:1]
            record.quantity_invoiced = latest_line.quantity if latest_line else 0.0

    @api.depends('total_days', 'quantity_invoiced')
    def _compute_quantity_to_invoice(self):
        for record in self:
            record.quantity_to_invoice = record.total_days - record.quantity_invoiced

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

    def unlink(self):
        for record in self:
            self.env['rental_and_lease.management'].search([
                ('property_id', '=', record.id)
            ]).unlink()
