from odoo import fields, models, api


class Property(models.Model):
    _name = "property.management"
    _description = "property management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "property_name"

    property_name = fields.Char(required=True)
    property_image = fields.Image()
    street1 = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    country_id = fields.Many2one('res.country')
    state_id = fields.Many2one('res.country.state', 'Fed. State', domain="[('country_id', '=?', country_id)]")
    can_be_sold = fields.Boolean()
    legal_amount = fields.Float()
    rent = fields.Float(readonly=False, store=True)
    description = fields.Text()
    owner_id = fields.Many2one('res.partner')
    built_date = fields.Date()
    facility_ids = fields.Many2many('property.facilities', string="Facilities")
    rent_or_lease_id = fields.Many2one('property.line')
    property_type_id = fields.Many2one('rental_and_lease.management')
    owned_property_ids = fields.One2many('res.partner', 'owner_property_ids')
    property_rent_leas_ids = fields.One2many('rental_and_lease.management', 'property_id')
    rental_lease_count = fields.Integer(string="Rental/Lease Count", compute="_compute_rental_lease_count")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('rented', 'Rented'),
            ('leased', 'Leased'),
            ('sold', 'Sold')
        ], tracking=True, default='draft'
    )
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  compute='_compute_currency_id',
                                  readonly=False, required=True, store=True,
                                  precompute=True)
    currency_symbol = fields.Char(related='currency_id.symbol')

    @api.depends('company_id')
    def _compute_currency_id(self):
        for program in self:
            program.currency_id = (program.company_id.currency_id or
                                   program.currency_id)

    def unlink(self):
        for record in self:
            # Find all property.line records that use this property
            related_lines = self.env['property.line'].search([
                ('property_id', '=', record.id)
            ])
            # Delete only the related lines, not the whole rent order
            related_lines.unlink()
        return super(Property, self).unlink()

    def _compute_rental_lease_count(self):
        for record in self:
            record.rental_lease_count = self.env['property.line'].search_count(
                [('property_id', '=', self.id)])

    def action_get_rent_and_lease(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rent/lease',
            'view_mode': 'list,form',
            'res_model': 'property.line',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    @api.model
    def get_property_amount(self, property_id, type):
        property = self.browse(int(property_id))
        if not property.exists():
            return 0
        if type == 'rental':
            return property.rent
        elif type == 'lease':
            return property.legal_amount
        return 0


class Facilities(models.Model):
    _name = "property.facilities"
    _description = "Property facilities"
    _rec_name = "facility"

    facility = fields.Char(required=True)
