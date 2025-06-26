# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import ValidationError


class RentAndLease(models.Model):
    _name = "rental_and_lease.management"
    _rec_name = "sequence"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    property_id = fields.Many2one('property.management')
    type = fields.Selection([
        ('rental', 'Rental'),
        ('lease', 'Lease'),
    ], default='rental')
    tenant_id = fields.Many2one('res.partner', string="Tenant", required=True)
    sequence = fields.Char(string="Reference Number", readonly=True)
    attchment_ids = fields.Many2many('ir.attachment', compute='_compute_attachment')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    total_days = fields.Integer(compute='_compute_days')
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    amount = fields.Float(compute="_compute_amount")
    total = fields.Float(compute="_compute_total_amount")
    property_ids = fields.One2many("property.line", "property_rent_lease_id")
    new_invoice_id = fields.Many2many('account.move', string='Invoice')
    is_invoice_paid = fields.Boolean(string="Invoice Paid", compute="_compute_invoice_paid")
    invoiced_ids = fields.Many2many('account.move', compute='_compute_invoiced')
    invoice_count = fields.Integer(string="invoices", compute='compute_invoice_count', default=0)
    invoice_ids = fields.One2many('account.move', 'rent_lease_id', string='Invoices')
    invoice_state = fields.Boolean(string="Invoice state", compute="_compute_invoice_state")
    invoice = fields.Many2one('account.move')
    invoice_line_ids = fields.One2many('account.move.line', 'property_line_id')
    is_remaining_to_invoice = fields.Boolean(compute='_compute_is_remaining_to_invoice')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('closed', 'Closed'),
            ('returned', 'Returned'),
            ('expired', 'Expired'),
        ], default='draft', tracking=True
    )

    def _compute_invoiced(self):
        for record in self:
            invoiced_ids = self.env['account.move'].search([
                ('rent_lease_id', '=', self.id),
                ('state', '=', 'posted')
            ])
            record.invoiced_ids = invoiced_ids

    @api.depends('property_ids.quantity_invoiced', 'property_ids.total_days')
    def _compute_is_remaining_to_invoice(self):
        for record in self:
            record.is_remaining_to_invoice = any(
                line.total_days > line.quantity_invoiced for line in record.property_ids
            )


    def action_create_invoice(self):
        for record in self:
            # invoiced = self.env['account.move'].search([
            #     ('rent_lease_id', '=', record.id),
            #     ('state', '=', 'posted')
            # ])
            # if invoiced:
            #     raise ValidationError("Invoice already created.")

            draft_invoice = self.env['account.move'].search([
                ('rent_lease_id', '=', record.id),
                ('state', '=', 'draft'),

            ], limit=1)

            existing_property = []
            if draft_invoice:
                existing_property = draft_invoice.invoice_line_ids.mapped('name')

            invoice_lines = []
            for line in record.property_ids:
                    if line.property_id.property_name not in existing_property:
                        invoice_lines.append(fields.Command.create({
                            'name': line.property_id.property_name,
                            'quantity': line.quantity_to_invoice,
                            'price_unit': line.amount or 0.0,
                            'property_line_id': line.id,
                        }))

        if draft_invoice:
            if invoice_lines:
                draft_invoice.write({
                    'invoice_line_ids': invoice_lines
                })
            invoice = draft_invoice
        else:
            invoice = self.env['account.move'].create({
                'partner_id': record.tenant_id.id,
                'invoice_date': fields.Date.today(),
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
                'rent_lease_id': record.id,
            })
            record.invoiced_ids = [fields.Command.link(invoice.id)]

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current'
        }

    def compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count([('rent_lease_id', '=', self.id)])

    def action_get_rent_and_lease_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('rent_lease_id', '=', self.id)],
            'context': {'create': False}
        }

    @api.depends('type', 'property_id.rent', 'property_id.legal_amount')
    def _compute_amount(self):
        for record in self:
            if record.type == 'rental':
                record.amount = record.property_id.rent or 0.0
            elif record.type == 'lease':
                record.amount = record.property_id.legal_amount or 0.0
            else:
                record.amount = 0.0

    @api.depends('property_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total = sum(record.property_ids.mapped("total_amount"))

    @api.depends('start_date', 'end_date')
    def _compute_days(self):
        for record in self:
            start = record.start_date
            end = record.end_date
            if isinstance(start, date) and isinstance(end, date):
                record.total_days = abs((end - start).days)
            else:
                record.total_days = 0

    def _compute_attachment(self):
        for record in self:
            attachment_ids = self.env['ir.attachment'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id)
            ])
            record.attachment_ids = attachment_ids

    def action_confirmed(self):
        for record in self:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id)
            ])
            if attachments:
                record.state = "confirmed"
            else:
                raise ValidationError("Attach a file to confirm.")

    def action_closed(self):
        for record in self:
            record.state = "closed"
        return True

    def action_returned(self):
        for record in self:
            record.state = "returned"
        return True

    def action_expired(self):
        for record in self:
            record.state = "expired"
        return True

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('property.property')
        return super(RentAndLease, self).create(vals)

    def _compute_invoice_paid(self):
        for record in self:
            record.is_invoice_paid = all(invoice.payment_state == 'paid' for invoice in record.invoiced_ids)

    def _compute_invoice_state(self):
        for record in self:
            record.invoice_state = record.invoiced_ids.state == 'posted'
            if record.invoice_state == True:
                body = _('Invoice %s is Posted', self.invoiced_ids.name)
                record.message_post(body=body)
