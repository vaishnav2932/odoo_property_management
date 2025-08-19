/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    async pay() {
        const orm = this.env.services.orm;
        const config_id = this.config.id;
        let session_discount = 0;
        let max_discount_limit = 0;
        try {
            max_discount_limit = await orm.call(
                'ir.config_parameter',
                'get_param',
                ['pos_rating.discount_limit']
            );
            max_discount_limit = parseFloat(max_discount_limit || 0) * 100;
            const set_max_discount = await orm.call(
                 'ir.config_parameter',
                 'get_param',
                 ['pos_rating.set_max_discount']
            )
            const result = await orm.call('res.config.settings', 'get_current_session_orders', [config_id]);
            if (Array.isArray(result)) {
                result.forEach(order => {
                    if (order.lines && Array.isArray(order.lines)) {
                        order.lines.forEach(line => {
                            const product_discount = line.discount;
                            session_discount += product_discount;
                        });
                    }
                });
            }
            const order = this.get_order();
            const order_lines = order.get_orderlines();
            let line_discount = 0;
            for (const line of order_lines) {
                line_discount += line.get_discount();
            }
            const total_discount = (line_discount + session_discount);
            if (total_discount > max_discount_limit && set_max_discount) {
                await this.dialog.add(AlertDialog, {
                    title: _t("Discount limit exceeded"),
                    body: _t("The total discount for products exceeded the maximum discount limit."),
                });
                return false;
            }
        } catch (err) {
            console.error("Error fetching current session orders or discount limit:", err);
        }
        return super.pay(...arguments);
    },
});
