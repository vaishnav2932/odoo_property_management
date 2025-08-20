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
            str(payu_values['key']),
            str(payu_values['txnid']),
            str(payu_values['amount']),
            str(payu_values['productinfo']),
            str(payu_values['firstname']),
            str(payu_values['email']),
            '', '', '', '', '', '', '', '', '', '',  # udf1–udf10
            self.provider_id.payu_salt,
        ])

        payu_values['hash'] = hashlib.sha512(hash_seq.encode('utf-8')).hexdigest().lower()

        return {
            'api_url': api_url,
            'payumoney_values': payu_values,
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Find the transaction record using PayU's txnid."""
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'payu' or len(tx) == 1:
            return tx

        reference = notification_data.get('txnid')
        if not reference:
            raise ValidationError(_("PayU: Received data with missing txnid."))

        tx = self.search([
            ('reference', '=', reference),
            ('provider_code', '=', 'payu')
        ])
        if not tx:
            raise ValidationError(_("PayU: No transaction found matching reference %s.") % reference)
        return tx

    # def _process_notification_data(self, notification_data):
    #     """Validate PayU response and update transaction state."""
    #     res = super()._process_notification_data(notification_data)
    #
    #     if self.provider_code != 'payu':
    #         return res
    #
    #     provider = self.provider_id
    #     salt = provider.payu_salt
    #     key = provider.payu_merchant_key
    #     status = notification_data.get('status', '')
    #
    #     # Build reverse hash according to PayU spec
    #     parts = [salt, status]
    #     for i in range(10, 0, -1):  # udf10 → udf1
    #         parts.append(notification_data.get(f'udf{i}', '') or '')
    #     parts += [
    #         notification_data.get('email', ''),
    #         notification_data.get('firstname', ''),
    #         notification_data.get('productinfo', ''),
    #         str(notification_data.get('amount', '')),
    #         notification_data.get('txnid', ''),
    #         key,
    #     ]
    #
    #     expected_hash = hashlib.sha512('|'.join(parts).encode('utf-8')).hexdigest().lower()
    #     received_hash = (notification_data.get('hash') or '').lower()
    #
    #     if expected_hash != received_hash:
    #         raise ValidationError(_("PayU: Invalid hash received."))
    #
    #     # Update transaction state based on status
    #     if status == 'success':
    #         self._set_done()
    #     elif status == 'failure':
    #         self._set_canceled()
    #     else:
    #         self._set_error(_("PayU: Payment status %s") % status)
    #
    #     return True
