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
        query = f"""
             SELECT
                crm_team.name AS team_name,
                COUNT(sale_order.id) AS total_orders,
                SUM(amount_total) AS total_amount
             FROM
                crm_team
             LEFT JOIN
                 sale_order ON sale_order.team_id = crm_team.id
             GROUP BY
                crm_team.name
             ORDER BY
                crm_team.name;      
        """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_sales_person(self):
        query = f"""
             SELECT
                    res_partner.name AS user_name,
                    COUNT(sale_order.id) AS total_orders,
                    SUM(amount_total) AS total_amount
                FROM 
                    sale_order
                INNER JOIN
                    res_users ON sale_order.user_id = res_users.id
                INNER JOIN
                    res_partner ON res_users.partner_id = res_partner.id
                GROUP BY
                    res_partner.name
                ORDER BY
                    res_partner.name;
             """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_top_customer(self):
        query = f"""
               SELECT 
                    res_partner.name AS partner,
                    COUNT(sale_order.id) AS total_orders,
                    SUM(amount_total) AS total_amount
                FROM 
                   sale_order
                INNER JOIN
                   res_partner on sale_order.partner_id = res_partner.id
                GROUP BY
                   res_partner.name
                ORDER BY
                   total_amount DESC;
            """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_lowest_selling_product(self):
        query = f"""
                   SELECT 
                        name,SUM(price_total) AS total
                   FROM
                       sale_order_line
                   GROUP BY
                       name
                   ORDER BY
                       total DESC;
           """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_highest_selling_product(self):
        query = f"""
                   SELECT 
                        name,SUM(price_total) AS total
                   FROM
                       sale_order_line
                   GROUP BY
                       name
                   ORDER BY
                       total;
               """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_order_status(self):
        query = f"""
                 SELECT 
                   state,
                   COUNT(state) AS state_count
                 FROM 
                   sale_order   
                 GROUP BY
                    state;
                 """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_invoice_status(self):
        query = f"""
                SELECT 
                   invoice_status,
                   COUNT(invoice_status) 
                FROM 
                   sale_order
                GROUP BY
                   invoice_status;
                """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
