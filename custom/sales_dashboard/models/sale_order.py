# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.tools import date_utils

from datetime import date, datetime, time


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
            ('state', '=', 'draft')
        ])
        total_revenue = sum(sale_order.mapped('amount_total'))
        return {
            'total_sale_order': len(sale_order),
            'total_quotation': len(quotations),
            'total_revenue': total_revenue,
        }

    # sales team orders


    @api.model
    def get_team_day_order(self):
        query = """
             SELECT
                crm_team.name AS team_name,
                COUNT(sale_order.id) AS total_orders,
                SUM(sale_order.amount_total) AS total_amount
            FROM
                crm_team
            LEFT JOIN
                sale_order ON sale_order.team_id = crm_team.id
            WHERE
                DATE(sale_order.create_date) = CURRENT_DATE
            GROUP BY
                crm_team.name
            ORDER BY
                crm_team.name;
       """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_month_orders_by_team(self):
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0,
                                   microsecond=0)
        next_month = start_date + relativedelta(months=1)
        query = """
             SELECT
                    crm_team.name AS team_name,
                    COUNT(sale_order.id) AS total_orders,
                    SUM(sale_order.amount_total) AS total_amount
                FROM
                    crm_team
                LEFT JOIN
                     sale_order ON sale_order.team_id = crm_team.id
                WHERE
                    sale_order.create_date >= %s
                    AND sale_order.create_date < %s
                GROUP BY
                    crm_team.name
                ORDER BY
                   crm_team.name;
        """
        self.env.cr.execute(query,
                            (start_date, next_month))
        return self.env.cr.dictfetchall()

    @api.model
    def get_team_custom_orders(self, from_date, to_date):
        query = """
            SELECT
                crm_team.name AS team_name,
                COUNT(sale_order.id) AS total_orders,
                SUM(sale_order.amount_total) AS total_amount
            FROM
                crm_team
            LEFT JOIN
                sale_order ON sale_order.team_id = crm_team.id
            WHERE
                sale_order.create_date >= %s
                AND sale_order.create_date < %s
            GROUP BY
                crm_team.name
            ORDER BY
                crm_team.name;
        """
        # Add +1 day to include full `to_date`
        to_date_plus = fields.Date.from_string(to_date) + relativedelta(days=1)
        self.env.cr.execute(query, (from_date, to_date_plus))
        return self.env.cr.dictfetchall()

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
    # sales person order
    @api.model
    def get_sale_person_day_order(self):
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
                        WHERE
                            DATE(sale_order.create_date) = CURRENT_DATE
                        GROUP BY
                            res_partner.name
                        ORDER BY
                            res_partner.name;
                     """
            self.env.cr.execute(query)
            return self.env.cr.dictfetchall()

    @api.model
    def get_sale_person_month_order(self):
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0,
                                   microsecond=0)
        next_month = start_date + relativedelta(months=1)
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
                    WHERE
                        sale_order.create_date >= %s
                        AND sale_order.create_date < %s
                    GROUP BY
                        res_partner.name
                    ORDER BY
                        res_partner.name;
                 """
        self.env.cr.execute(query,
                            (start_date, next_month))
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

    #  lowest selling product
    @api.model
    def get_lowest_monthly_selling_product(self):
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0,
                                   microsecond=0)
        next_month = start_date + relativedelta(months=1)
        query = f"""
                  SELECT 
                       name,SUM(price_total) AS total,
                       COUNT(sale_order_line.id) AS total_orders
                  FROM
                      sale_order_line     
                  WHERE
                        sale_order_line.create_date >= %s
                        AND sale_order_line.create_date < %s
                  GROUP BY
                      name
                  ORDER BY
                      total DESC;
              """
        self.env.cr.execute(query,
                            (start_date, next_month))
        return self.env.cr.dictfetchall()

    @api.model
    def get_lowest_daily_selling_product(self):
        query = f"""
                      SELECT 
                           name,SUM(price_total) AS total,
                           COUNT(sale_order_line.id) AS total_orders
                      FROM
                          sale_order_line     
                      WHERE
                          DATE(sale_order_line.create_date) = CURRENT_DATE
                      GROUP BY
                          name
                      ORDER BY
                          total DESC,
                          total_orders DESC;
                  """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_lowest_selling_product(self):
        query = f"""
                   SELECT 
                        name,SUM(price_total) AS total,
                        COUNT(sale_order_line.id) AS total_orders

                   FROM
                       sale_order_line     
                   GROUP BY
                       name
                   ORDER BY
                       total DESC;
               """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    # highest selling product
    @api.model
    def get_highest_daily_selling_product(self):
        query = f"""
                   SELECT 
                        name,SUM(price_total) AS total,
                        COUNT(sale_order_line.id) AS total_orders
                   FROM
                       sale_order_line
                   WHERE
                       DATE(sale_order_line.create_date) = CURRENT_DATE
                   GROUP BY
                       name
                   ORDER BY
                       total,
                       total_orders;
                   """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_highest_monthly_selling_product(self):
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0,
                                   microsecond=0)
        next_month = start_date + relativedelta(months=1)
        query = f"""
                   SELECT 
                        name,SUM(price_total) AS total,
                        COUNT(sale_order_line.id) AS total_orders
                   FROM
                       sale_order_line
                   WHERE
                        sale_order_line.create_date >= %s
                        AND sale_order_line.create_date < %s
                   GROUP BY
                       name
                   ORDER BY
                       total,
                       total_orders;
                   """
        self.env.cr.execute(query,
                            (start_date, next_month))
        return self.env.cr.dictfetchall()

    @api.model
    def get_highest_selling_product(self):
        query = f"""
                   SELECT 
                        name,SUM(price_total) AS total,
                        COUNT(sale_order_line.id) AS total_orders
                   FROM
                       sale_order_line
                   GROUP BY
                       name
                   ORDER BY
                       total,
                       total_orders ASC;
               """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    #  sale order status
    @api.model
    def get_order_daily_status(self):
        query = f"""
                 SELECT 
                   state,
                   COUNT(state) AS state_count,
                   SUM(amount_total) AS total_amount
                 FROM 
                   sale_order   
                 WHERE
                    DATE(sale_order.create_date) = CURRENT_DATE  
                 GROUP BY
                    state;
                 """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    @api.model
    def get_order_monthly_status(self):
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0,
                                   microsecond=0)
        next_month = start_date + relativedelta(months=1)
        query = f"""
                 SELECT 
                   state,
                   COUNT(state) AS state_count,
                   SUM(amount_total) AS total_amount
                 FROM 
                   sale_order   
                 WHERE
                    sale_order.create_date >= %s
                    AND sale_order.create_date < %s
                 GROUP BY
                    state;
                 """
        self.env.cr.execute(query,
                            (start_date, next_month))
        return self.env.cr.dictfetchall()
    @api.model
    def get_order_status(self):
        query = f"""
                 SELECT 
                   state,
                   COUNT(state) AS state_count,
                   SUM(amount_total) AS total_amount
                 FROM 
                   sale_order   
                 GROUP BY
                    state;
                 """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    # invoice status
    @api.model
    def get_invoice_daily_status(self):
        query = f"""
                SELECT 
                   invoice_status,
                   COUNT(invoice_status),
                   SUM(amount_total) AS total_amount
                FROM 
                   sale_order
                WHERE
                    DATE(sale_order.create_date) = CURRENT_DATE  
                GROUP BY
                   invoice_status;
                """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
    @api.model
    def get_invoice_monthly_status(self):
        today = datetime.today()
        start_date = today.replace(day=1, hour=0, minute=0, second=0,
                                   microsecond=0)
        next_month = start_date + relativedelta(months=1)
        query = f"""
                SELECT 
                   invoice_status,
                   COUNT(invoice_status),
                   SUM(amount_total) AS total_amount
                FROM 
                   sale_order
                WHERE
                    sale_order.create_date >= %s
                    AND sale_order.create_date < %s
                GROUP BY
                   invoice_status;
                """
        self.env.cr.execute(query,
                            (start_date, next_month))
        return self.env.cr.dictfetchall()

    @api.model
    def get_invoice_status(self):
        query = f"""
                    SELECT 
                       invoice_status,
                       COUNT(invoice_status),
                       SUM(amount_total) AS total_amount
                    FROM 
                       sale_order
                    GROUP BY
                       invoice_status;
                    """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()


