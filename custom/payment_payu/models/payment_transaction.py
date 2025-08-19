import hashlib

from werkzeug import urls
from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.addons.payment import utils as payment_utils


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'payu':
            return res

        first_name, last_name = payment_utils.split_partner_name(
            self.partner_id.name or ""
        )

        api_url = 'https://test.payu.in/_payment'
        payu_return_path = '/payment/payumoney/return'

        # Always ensure amount is string with 2 decimals
        amount_str = "%.2f" % self.amount

        payu_values = {
            'key': self.provider_id.payu_merchant_key,
            'txnid': self.reference,
            'amount': amount_str,
            'productinfo': "Order-%s" % self.reference,
            'firstname': first_name,
            'email': self.partner_email,
            'phone': self.partner_phone or "",
            'surl': urls.url_join(self.get_base_url(), '/payment/payumoney/success'),
            'furl': urls.url_join(self.get_base_url(), '/payment/payumoney/failure'),
        }

        # Construct hash
        hash_seq = "|".join([
            payu_values['key'],
            payu_values['txnid'],
            payu_values['amount'],
            payu_values['productinfo'],
            payu_values['firstname'],
            payu_values['email'],
            '', '', '', '', '', '', '', '', '', '',  # udf1–udf10
            self.provider_id.payu_salt,
        ])
        payu_values['hash'] = hashlib.sha512(hash_seq.encode('utf-8')).hexdigest().lower()

        return {
            'api_url': api_url,
            'payumoney_values': payu_values,
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code,
                                                    notification_data)
        if provider_code != 'payu' or len(tx) == 1:
            return tx

        reference = notification_data.get('txnid')
        if not reference:
            raise ValidationError(
                "PayUmoney: " + _("Received data with missing reference (%s)",
                                  reference)
            )
        tx = self.search(
            [('reference', '=', reference), ('provider_code', '=', 'payu')])
        if not tx:
            raise ValidationError(
                "PayUmoney: " + _("No transaction found matching reference %s.",
                                  reference)
            )
        return tx
