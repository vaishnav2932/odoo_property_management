# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ExampleLine(models.Model):
    """for the example line """
    _name = 'example.line'
    _description = 'Example line'

    example_id = fields.Many2one('example.example', string="Example")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer(string="Quantity")
    price = fields.Float(string="Price")
