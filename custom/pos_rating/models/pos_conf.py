# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    set_max_discount = fields.Boolean("Set maximum discount")
    discount_limit = fields.Float(string="Maximum discount limit")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        set_max_discount = icp_sudo.get_param(
            'pos_rating.set_max_discount')
        discount_limit = icp_sudo.get_param(
            'pos_rating.discount_limit')
        res.update(
            set_max_discount=set_max_discount,
            discount_limit=discount_limit
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'pos_rating.set_max_discount', self.set_max_discount)
        self.env['ir.config_parameter'].sudo().set_param(
            'pos_rating.discount_limit',
            self.discount_limit)
        return res

    @api.model
    def get_current_session_orders(self, config_id):
        config = self.env['pos.config'].browse(config_id)

        if not config.current_session_id:
            return []
        orders = self.env['pos.order'].search([
            ('session_id', '=', config.current_session_id.id)
        ])
        data = []
        for order in orders:
            order_data = {
                'id': order.id,
                'name': order.name,
                'partner_id': order.partner_id.id if order.partner_id else False,
                'date_order': order.date_order,
                'amount_total': order.amount_total,
                'lines': []
            }
            for line in order.lines:
                order_data['lines'].append({
                    'id': line.id,
                    'product_id': line.product_id.id,
                    'product_name': line.product_id.display_name,
                    'qty': line.qty,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'price_subtotal': line.price_subtotal,
                    'price_subtotal_incl': line.price_subtotal_incl,
                })
            data.append(order_data)
        return data
