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
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
    ], string='Payment State', compute='_compute_payment_state', store=True)
    invoiced_ids = fields.Many2many('account.move', compute='_compute_invoiced')
    invoice_count = fields.Integer(string="invoices", compute='compute_invoice_count', default=0)
    invoice_ids = fields.One2many('account.move', 'rent_lease_id', string='Invoices')
    invoice_state = fields.Boolean(string="Invoice state", compute="_compute_invoice_state")
    invoice = fields.Many2one('account.move')
    invoice_line_ids = fields.One2many('account.move.line', 'property_line_id')
    is_remaining_to_invoice = fields.Boolean(compute='_compute_is_remaining_to_invoice')
    is_fully_invoiced = fields.Boolean(compute="_compute_fully_invoiced")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('inapprove', 'In Approve'),
            ('approved', 'Approved'),
            ('confirmed', 'Confirmed'),
            ('closed', 'Closed'),
            ('returned', 'Returned'),
            ('expired', 'Expired'),
        ], default='draft', tracking=True
    )

    @api.depends('invoice_ids.payment_state')
    def _compute_payment_state(self):
        for record in self:
            states = record.invoice_ids.mapped('payment_state')
            if not states:
                record.payment_state = 'not_paid'
            elif all(state == 'paid' for state in states):
                record.payment_state = 'paid'
            elif any(state == 'in_payment' for state in states):
                record.payment_state = 'in_payment'
            elif any(state == 'partial' for state in states):
                record.payment_state = 'partial'
            else:
                record.payment_state = 'not_paid'

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

    def compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count([('rent_lease_id', '=', self.id)])

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

    def _compute_invoice_state(self):
        for record in self:
            record.invoice_state = record.invoiced_ids.state == 'posted'
            if record.invoice_state == True:
                body = _('Invoice %s is Posted', self.invoiced_ids.name)
                record.message_post(body=body)

    @api.depends('property_ids.invoice_line_ids.move_id.state', 'property_ids.invoice_line_ids.quantity',
                 'property_ids.total_days')
    def _compute_fully_invoiced(self):
        for rec in self:
            fully_invoiced = True
            for line in rec.property_ids:
                posted_invoice_lines = line.invoice_line_ids.filtered_domain([('move_id.state', '=', 'posted')])
                total_invoiced_qty = sum(posted_invoice_lines.mapped('quantity'))
                print(total_invoiced_qty)
                if total_invoiced_qty < line.total_days:
                    fully_invoiced = False
                    break
            rec.is_fully_invoiced = fully_invoiced

    def action_create_invoice(self):
        for record in self:
            draft_invoice = self.env['account.move'].search([
                ('rent_lease_id', '=', record.id),
                ('state', '=', 'draft'),
            ], limit=1)

            invoice_lines = []

            for line in record.property_ids:
                should_append = True
                if draft_invoice:
                    matching_line = draft_invoice.invoice_line_ids.filtered(
                        lambda l: l.property_line_id.id == line.id
                    )
                    if matching_line:
                        if matching_line.quantity != line.quantity_to_invoice:
                            matching_line.write({
                                'quantity': line.quantity_to_invoice,
                            })
                        should_append = False  # Don't add again
                if should_append:
                    invoice_lines.append(fields.Command.create({
                        'name': line.property_id.property_name,
                        'quantity': line.quantity_to_invoice,
                        'price_unit': line.amount or 0.0,
                        'property_line_id': line.id,
                    }))

            if draft_invoice:
                if invoice_lines:
                    draft_invoice.write({'invoice_line_ids': invoice_lines})
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

    def action_confirmed(self):
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)
        ])
        if attachments:
            if self.env.user.has_group(
                    'propertymanagement.property_group_user') and self.state != "approved":
                raise ValidationError("Need manager approval to confirm.")
            else:
                self.state = "confirmed"
                template = self.env.ref("propertymanagement.confirmation_mail")
                email_values = {'email_from': self.env.user.email}
                template.send_mail(self.id, force_send=True, email_values=email_values)
        else:
            raise ValidationError("Attach a file to confirm.")

    def action_to_approved(self):
        self.state = "inapprove"

    def action_approve(self):
        if self.env.user.has_group('propertymanagement.property_group_manager'):
            self.state = "approved"

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
            template = self.env.ref("propertymanagement.expiry_order")
            email_values = {'email_from': self.env.user.email}
            template.send_mail(self.id, force_send=True, email_values=email_values)
        return True

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('property.property')
        return super(RentAndLease, self).create(vals)

    def change_to_expire(self):
        today = date.today()
        records = self.search([
            ('end_date', '>=', today),
            ('state', '!=', 'expired')
        ])
        for record in records:
            record.state = 'expired'
        return True

    def payment_reminder(self):
        today = date.today()
        records = self.search([
            ('end_date', '=', today),
            ('state', '=', 'expired')
        ])
        for record in records:
            template = self.env.ref("propertymanagement.payment_reminder")
            email_values = {'email_from': self.env.user.email}
            template.send_mail(record.id, force_send=True, email_values=email_values)

    # def print_sample_report(self):
    #     data = {
    #
    #         'model_id': self.id,
    #         'to_date': self.start_date,
    #         'from_date': self.end_date,
    #         'property_id': self.property_id.id,
    #         'property_name': self.property_id.property_name
    #     }
    #     # docids = self.env['purchase.order'].search([]).ids
    #     return self.env.ref('propertymanagement.action_report_rent_lease_order').report_action(None, data=data)
