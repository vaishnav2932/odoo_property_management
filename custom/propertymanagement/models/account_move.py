# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    rent_lease_id = fields.Many2one('rental_and_lease.management', string='Rent/Lease Record')
    quantity_line_id = fields.Many2one('property.line')




