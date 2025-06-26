# encoding utf-8
from odoo import fields, models, api


class RentalAndLeaseInvoice(models.Model):
    _inherit = "rentalandlease.management"

    invoice_count = fields.Integer(string="invoices", compute='compute_invoice_count', default=0)
    invoice_ids = fields.One2many('account.move', 'rent_lease_id', string='Invoices')
    invoice = fields.Many2one('account.move')

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



