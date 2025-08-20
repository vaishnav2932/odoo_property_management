# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PayUPaymentController(http.Controller):

    @http.route(['/payment/payumoney/success', '/payment/payumoney/failure'], type='http', auth='public', csrf=False)
    def payu_return(self, **post):
        """Handle PayU return (browser redirect)."""
        _logger.info("PayU return received: %s", post)

        tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('payu', post)
        if not tx:
            return request.redirect('/payment/status?error=transaction_not_found')

        try:
            tx._handle_notification_data('payu', post)
        except Exception as e:
            _logger.exception("Error handling PayU return: %s", e)
            return request.redirect('/payment/status?error=notification_failed')

        return request.redirect('/payment/status?success=1')

    @http.route(['/payment/payumoney/notify'], type='http', auth='public', csrf=False)
    def payu_notify(self, **post):
        """Server-to-server notify from PayU."""
        _logger.info("PayU notify received: %s", post)

        tx = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('payu', post)
        if not tx:
            return "NOTOK"

        try:
            tx._handle_notification_data('payu', post)
        except Exception as e:
            _logger.exception("Error handling PayU notify: %s", e)
            return "NOTOK"

        return "OK"
