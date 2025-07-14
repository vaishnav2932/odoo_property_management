# -*- coding: utf-8 -*-from
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_id = fields.Many2one('sale.order.line')
    milestone = fields.Integer(related="sale_order_id.milestone")

    def create_project(self):
        project = self.env['project.project'].create({
            'name': self.name
        })
        for product, line in enumerate(self.order_line):
            line.milestone = (product // 2) + 1
        milestone_dict = {}
        for line in self.order_line:
            if line.milestone:
                milestone_dict.setdefault(line.milestone, []).append(line)

        stage = self.env['project.task.type'].search([
            ('name', '=', 'New'),
            ('project_ids', 'in', project.id)
        ], limit=1)

        if not stage:
            stage = self.env['project.task.type'].create({
                'name': 'New',
                'project_ids': [(4, project.id)],
            })

        for num, lines in milestone_dict.items():
            parent_task = self.env['project.task'].create({
                'name': f'Milestone {num}',
                'project_id': project.id,
                'partner_id': self.partner_id.id,
                'stage_id': stage.id,

            })
            for line in lines:
                self.env['project.task'].create({
                    'name': f'Milestone {num} - {line.product_id.name}',
                    'project_id': project.id,
                    'parent_id': parent_task.id,
                    'partner_id': self.partner_id.id,
                    'stage_id': stage.id,

                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': project.id,
            'target': 'current'
        }

