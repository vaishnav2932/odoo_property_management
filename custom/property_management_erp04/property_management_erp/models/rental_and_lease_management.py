# encoding utf-8
from odoo import fields, models, api, _
from datetime import date, datetime

from odoo.api import ondelete
from odoo.exceptions import ValidationError


class RentAndLease(models.Model):
    _name = "rental_and_lease.management"
    _rec_name = "sequence"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    property_id = fields.Many2one('property.management', ondelete='cascade')
    type = fields.Selection([
        ('rental', 'Rental'),
        ('lease', 'Lease'),
    ], default='rental')
    tenant_id = fields.Many2one('res.partner', string="Tenant", required=True)
    sequence = fields.Char(string="Reference Number", readonly=True)
    attchment_ids = fields.Many2many('ir.attachment', compute='_compute_attachment')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id, ondelete='cascade')
    total_days = fields.Integer(compute='_compute_days')
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    amount = fields.Float(compute="_compute_amount")
    total = fields.Float(compute="_compute_total_amount")
    property_ids = fields.One2many("property.line", "property_rent_lease_id", ondelete='cascade')
    name_ids = fields.Many2many('property.line', ondelete='cascade')
    new_invoice_id = fields.Many2one('account.move', string='Invoice')
    is_invoice_paid = fields.Boolean(string="Invoice Paid", compute="_compute_invoice_paid")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('closed', 'Closed'),
            ('returned', 'Returned'),
            ('expired', 'Expired'),
        ], default='draft', tracking=True
    )

    def action_create_invoice(self):
        self.ensure_one()
        invoice_lines = []
        for line in self.property_ids:
            invoice_lines.append((0, 0, {
                'name': line.property_id.property_name,
                'quantity': line.total_days or 1,
                'price_unit': line.amount or 0.0,
            }))
        invoice = self.env['account.move'].create({
            'partner_id': self.tenant_id.id,
            'invoice_date': fields.Date.today(),
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_lines,
            'rent_lease_id': self.id,  # Link invoice to Rent/Lease
        })
        self.new_invoice_id = invoice.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
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
                raise ValidationError("attach a file to confirm.")

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

    @api.depends('new_invoice_id.payment_state')
    def _compute_invoice_paid(self):
        for record in self:
            record.is_invoice_paid = record.new_invoice_id.payment_state == 'paid'
            if record.is_invoice_paid == True:
                body = _('Invoice %s is paid', self.new_invoice_id.name)
                record.message_post(body=body)
                break
