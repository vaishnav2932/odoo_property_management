from odoo import models, fields

class PropertyOwnerRecord(models.Model):
    _inherit = 'res.partner'

    property_id = fields.Many2one('property.management', string='Property')
    property_name = fields.Char(related='property_id.property_name', string='Property Name')

