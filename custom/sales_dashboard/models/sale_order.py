# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    currency_symbol = fields.Char(related='currency_id.symbol')

    @api.model
    def get_sale_order_data(self):
        sale_order = self.search([
            ('company_id', '=', self.env.company.id),
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'sale')
        ])
        quotations = self.search([
            ('company_id', '=', self.env.company.id),
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'draft'),
        ])
        total_revenue = sum(sale_order.mapped('amount_total'))

        return {
            'total_sale_order': len(sale_order),
            'total_quotation': len(quotations),
            'total_revenue': total_revenue,

        }
    @api.model
    def get_sales_team(self):
        sales_team = self.env['crm.team'].search([
        ])
        data = []
        for team in sales_team:
            team_data = {
                'sale_order_count': team.sale_order_count,
                'name': team.name,
                'invoiced': team.invoiced
            }
            data.append(team_data)
        return {
            'sales_team': data,
        }



