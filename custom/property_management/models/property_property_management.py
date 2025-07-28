# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class PropertyManagement(models.Model):
    """Creating a model of handling Rental or Lease management of the Properties with the fields Property ,
    Type which is rent/lease ,Tenant (Partner) ,Lease / Rent Amount ,Lease / Rent period (Start and end date)
     ,Add chatter"""
    _name = 'property.management'
    _description = "property management"
    _inherit = 'mail.thread'
    _rec_name = "reference_number"

    property_id = fields.Many2one('property.property', string="Property")
    property_type = fields.Selection(selection=[('rent', 'Rent'), ('lease', 'Lease')], default='rent')
    tenant_id = fields.Many2one('res.partner', string="Tenant",
                                help="a person who occupies land or property rented from a landlord.")
    rent_lease_amount = fields.Float('Rent/Lease Amount')
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('toapprove','To Approve'), ('confirmed', 'Confirmed'), ('closed', 'Closed'),
                   ('returned', 'Returned'), ('expired', 'Expired')], default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    total_days = fields.Integer(string="Total days", compute="_compute_total_days")
    total_amount = fields.Float(string="Total amount", compute="_compute_total_amount")
    reference_number = fields.Char(default='New', readonly=True, copy=False, string="Reference Number")
    properties_ids = fields.One2many('property.property.line', 'rent_lease_record_id', )
    total = fields.Float(string="Total", compute="_compute_total", store=True)
    invoice_count = fields.Integer(string="Invoice", compute='_compute_invoice_count', default=0)
    payment_ids = fields.Many2many('account.move', string="Payment state")
    payment_state = fields.Selection(related='payment_ids.payment_state', string="Payment state")
    is_invoiced = fields.Boolean(string="Is fully Invoiced", compute='_compute_is_invoiced')
    active = fields.Boolean(default=True)
    mail_sent_date = fields.Date()

    @api.depends("start_date", "end_date")
    def _compute_total_days(self):
        """to calculate total days from a range of days"""
        for rec in self:
            if rec.end_date:
                rec.total_days = abs((rec.end_date - rec.start_date).days)
            else:
                rec.total_days = 0

    @api.depends("total_days", "rent_lease_amount")
    def _compute_total_amount(self):
        """to calculate total amount from total days and rent/lease amount"""
        for rec in self:
            if rec.rent_lease_amount:
                rec.total_amount = rec.total_days * rec.rent_lease_amount
            else:
                rec.total_amount = 0

    @api.depends('properties_ids')
    def _compute_total(self):
        """to calculate total amount by summing all order line"""
        for rec in self:
            if rec.properties_ids:
                rec.total = sum(rec.properties_ids.mapped("total_amount"))
            else:
                rec.total = 0

    def _compute_invoice_count(self):
        """for getting invoice count in smart btn"""
        for record in self:
            record.invoice_count = len(record.payment_ids)

    @api.depends('properties_ids.invoice_line_ids.move_id.state', 'properties_ids.invoice_line_ids.quantity',
                 'properties_ids.total_days')
    def _compute_is_invoiced(self):
        """to check if the order is fully invoiced or not. and hide the create-invoice btn"""
        if self.properties_ids:
            for line in self.properties_ids:
                already_invoiced_qty = sum(line.invoice_line_ids.filtered(lambda l: l.move_id.state == 'posted').mapped(
                    'quantity'))
                remaining_qty = line.total_days - already_invoiced_qty
                if remaining_qty:
                    fully_invoiced = False
                else:
                    fully_invoiced = True
            self.is_invoiced = fully_invoiced
        else:
            self.is_invoiced = False

    @api.onchange("property_type", "property_id")
    def _onchange_property_id(self):
        """to find rent/lese amount when changing property or property type"""
        if self.property_type == "rent":
            self.rent_lease_amount = self.property_id.rent
        else:
            self.rent_lease_amount = self.property_id.legal_amount

    @api.model
    def create(self, vals):
        """Automatically generate a reference number"""
        vals['reference_number'] = self.env['ir.sequence'].next_by_code('property.management')
        return super(PropertyManagement, self).create(vals)

    def action_approve(self):
        if self.message_attachment_count:
            self.write({'state': 'confirmed'})
            self.send_mail()
        else:
            raise UserError("please attach related document before confirming")

    def action_confirm(self):
        """confirm btn"""
        if self.env.user.has_group('property_management.property_group_manager'):
            if self.message_attachment_count:
                self.write({'state': 'confirmed'})
                self.send_mail()
            else:
                raise UserError("please attach related document before confirming")
        else:
            self.write({'state': 'toapprove'})

    def action_close(self):
        """close btn"""
        self.write({'state': 'closed'})
        self.send_mail()

    def action_return(self):
        """return btn"""
        self.write({'state': 'returned'})
        self.send_mail()

    def action_expired(self):
        """expired btn"""
        self.write({'state': 'expired'})
        self.send_mail()

    def action_restore(self):
        """Restore btn"""
        self.write({'state': 'draft'})

    def action_invoice(self):
        """ button to create an invoice in the rent/lease form view based on the properties and amounts,
        and check whether there is already a draft invoice, if any, add the lines to the existing one.
        if all property line is invoiced and user again clicks the btn an alert will pop up.
        after confirming an invoice,if user adding another property to the property order line and creating invoice
        then invoice will be created only for the newly added property line.if invoiced quantity is less than
        ordered quantity in an order line and when user clicks create inv btn it should only create invoice
        for the remaining quantity"""
        invoice_lines = []
        for line in self.properties_ids:
            already_invoiced_qty = sum(line.invoice_line_ids.filtered(lambda l: l.move_id.state == 'posted').mapped('quantity'))
            remaining_qty = line.total_days - already_invoiced_qty
            existing_draft_line = line.invoice_line_ids.filtered(lambda l: l.move_id.state == 'draft')
            if remaining_qty > 0:
                if existing_draft_line:
                    existing_draft_line.write({
                        'quantity': remaining_qty
                    })
                else:
                    new_line = fields.Command.create({
                        'name': line.properties_id.name,
                        'quantity': remaining_qty,
                        'price_unit': line.rent_lease_amount,
                        'property_id': line.properties_id.id,
                    })
                    invoice_lines.append(new_line)
        existing_invoice = self.payment_ids.filtered(
            lambda r: r.state == 'draft' and r.move_type == 'out_invoice'
        )
        if invoice_lines:
            if existing_invoice:
                existing_invoice.write({
                    'invoice_line_ids': invoice_lines,
                })
                invoice = existing_invoice
                self.message_post(body="Draft invoice updated.")
            else:
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': self.tenant_id.id,
                    'rent_id': self.id,
                    'invoice_line_ids': invoice_lines,
                })
                self.payment_ids = [fields.Command.link(invoice.id)]
                self.message_post(body="New invoice created.")
        for inv_line in invoice.invoice_line_ids:
            line = self.properties_ids.filtered(lambda l: l.properties_id.id == inv_line.property_id.id)
            if line:
                line.invoice_line_ids = [fields.Command.link(inv_line.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_get_invoice(self):
        """invoice smart btn"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('rent_id', '=', self.id), ('move_type', '=', 'out_invoice')],
            'context': "{'create': False}"
        }

    def send_mail(self):
        """to send email for tenant when property order reaches in different stages.
         sending emails with scheduled action"""
        mail_template = self.env.ref('property_management.mail_template_status_change')
        mail_template.send_mail(self.id, force_send=True)

    def auto_expiry(self):
        """to set the property order as expired when it reaches due date,also sending mail"""
        today = fields.Date.today()
        record = self.env['property.management'].search([('end_date','=',today),('state','=','confirmed'),])
        for rec in record:
            rec.write({'state': 'expired'})
            rec.send_mail()

    def payment_followup(self):
        """to send Follow up on late payments from rent/lease management records based on due date by
         sending emails to the tenants, also preventing generating mail to the same order when clicking run manually"""
        today = fields.Date.today()
        record = self.env['property.management'].search([('state','=','confirmed'),('payment_state','!=','paid'),
                                                         ('mail_sent_date','!=',today)])
        for rec in record:
            followup_days = abs((rec.end_date - today).days)
            mail_template = rec.env.ref('property_management.mail_template_payment_follow_up').with_context(
                lang=rec.env.user.lang)
            if followup_days < 7:
                mail_template.send_mail(rec.id, force_send=True)
                rec.mail_sent_date = today