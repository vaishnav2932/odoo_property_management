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
        base_url = self.provider_id.get_base_url().rstrip('/')

        payu_values = {
            'txnid': self.reference,
            'amount': self.amount,
            'productinfo': "Order-%s" % self.reference,
            'firstname': first_name,
            'email': self.partner_email,
            'surl': f"{base_url}/payu/return",
            'furl': f"{base_url}/payu/return",
            'key': self.provider_id.payu_merchant_key,

        }
        print(payu_values)

        hash_seq = "|".join([
            str(payu_values['key']),
            str(payu_values['txnid']),
            str(payu_values['amount']),
            str(payu_values['productinfo']),
            str(payu_values['firstname']),
            str(payu_values['email']),
            '', '', '', '', '', '', '', '', '', '',
            str(self.provider_id.payu_salt),
        ])

        payu_values['hash'] = hashlib.sha512(hash_seq.encode('utf-8')).hexdigest().lower()

        return {
            'api_url': api_url,
            'payumoney_values': payu_values,
        }

    def _process_notification_data(self, notification_data):
        res = super()._process_notification_data(notification_data)

        if self.provider_code != 'payu':
            return res

        provider_ref = notification_data.get('mihpayid') or notification_data.get('txnid')
        print(provider_ref)
        if provider_ref:
            self.provider_reference = provider_ref

        status = notification_data.get('status', '')

        if status == 'success':
            self._set_done()

        elif status == 'failure':
            self._set_canceled()
        else:
            self._set_error(_("PayU: Payment status %s") % status)

        return True
