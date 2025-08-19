/** @odoo-module */
import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.get_property = publicWidget.Widget.extend({
    selector: '.properties_section',
    async willStart() {
        const result = await rpc('/get_property', {});
        if (result && result.properties) {
            const propertiesPerSlide = 4;
            const chunks = [];
            for (let i = 0; i < result.properties.length; i += propertiesPerSlide) {
                chunks.push(result.properties.slice(i, i + propertiesPerSlide));
            }
            const properties_carousel =  Math.random();
            this.$target.empty().html(renderToElement('property_management_erp.property_data', {
                chunks: chunks,
                properties_carousel: properties_carousel,
            }));
        }
    },
});

