# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    """used for creating invoice"""
    _inherit = "account.move"

    tenant_id = fields.Many2one('res.partner', string="Tenant")
    rent_id = fields.Many2one('property.management')

