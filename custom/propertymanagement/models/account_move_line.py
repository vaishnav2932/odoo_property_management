# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    property_line_id = fields.Many2one('property.line')
