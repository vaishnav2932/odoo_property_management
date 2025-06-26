# -*- coding: utf-8 -*-
from odoo import models, fields


class PropertyOwnerRecord(models.Model):
    _inherit = 'res.partner'

    owner_property_ids = fields.One2many('property.management', 'owner_id', string='Property')
