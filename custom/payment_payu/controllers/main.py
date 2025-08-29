# payment_payu/controllers/main.py
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PayUController(http.Controller):

    @http.route('/payu/return', type='http', auth='public', csrf=False,
                website=True)
    def payu_return(self, **post):
        print(post)
        """Customer is redirected here after payment."""
        txid = post.get('txnid')
        print("txid: ", txid)
        tx = request.env['payment.transaction'].sudo().search(
            [('reference', '=', txid)], limit=1)
        print(tx)
        if tx:
            tx._process_notification_data(post)
            return request.redirect('/payment/status')
        return request.redirect('/shop')
