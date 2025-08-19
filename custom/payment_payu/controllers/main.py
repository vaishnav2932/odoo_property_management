from odoo import http
from odoo.http import request
import hashlib

class PayUController(http.Controller):

    @http.route('/payment/payumoney/return', type='http', auth='public', methods=['POST'], csrf=False)
    def payu_return(self, **post):
        tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('payu', post)

        provider = tx.provider_id
        salt = provider.payu_salt
        key = provider.payu_merchant_key
        status = post.get('status', '')

        # Build reverse hash as per PayU spec
        parts = [salt, status]
        for i in range(10, 0, -1):
            parts.append(post.get(f'udf{i}', '') or '')
        parts += [
            post.get('email', ''),
            post.get('firstname', ''),
            post.get('productinfo', ''),
            str(post.get('amount', '')),
            post.get('txnid', ''),
            key,
        ]
        expected_hash = hashlib.sha512('|'.join(parts).encode('utf-8')).hexdigest().lower()
        received_hash = (post.get('hash') or '').lower()

        if expected_hash != received_hash:
            tx._set_error('PayU: hash mismatch')
            return request.redirect('/payment/status')

        if status == 'success':
            tx._set_done()
        elif status in ('failure', 'failed', 'cancelled'):
            tx._set_canceled()
        else:
            tx._set_pending(f'PayU: status {status}')

        return request.redirect('/payment/status')
