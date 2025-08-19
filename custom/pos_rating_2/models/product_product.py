# -*- coding: utf-8 -*-
from odoo import models,fields

class Product(models.Model):
    _inherit = 'product.product'

    rating = fields.Selection(
        [
            ('1','1'),
            ('2','2'),
            ('3','3'),
            ('4','4'),
            ('5','5')
        ],string="Rating", stor=True
    )

    def _load_pos_data_fields(self, config_id):
        data = super()._load_pos_data_fields(config_id)
        data += ['rating']
        return data









