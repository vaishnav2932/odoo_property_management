# -*- coding: utf-8 -*
from datetime import time
from odoo import _, fields, models, api
from odoo.addons.payment_paypal import const



class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('payu', "PayU")], ondelete={'payu': 'set default'})

    payu_merchant_key = fields.Char(
        string="Payu Merchant Key",
        help="The key solely used to identify the account with Payu.",
    )
    payu_salt = fields.Char(
        string="Payu Salt Key ",
        groups='base.group_system'
    )


    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'payu':
            return default_codes
        return const.DEFAULT_PAYMENT_METHOD_CODES

