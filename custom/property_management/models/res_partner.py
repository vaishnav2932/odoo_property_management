# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields


class ResPartner(models.Model):
    """for showing the property and rent/lease status in partner"""
    _inherit = "res.partner"

    properties_ids = fields.One2many('property.property', 'owner_id')
