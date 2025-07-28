# -*- coding: utf-8 -*-
from odoo import models, fields


class PropertyFacility(models.Model):
    """for adding facilities to property"""
    _name = 'property.facility'
    _description = 'Property facilities'

    name = fields.Char(string="Facilities")