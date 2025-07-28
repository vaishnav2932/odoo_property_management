import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from '@web/core/network/rpc';

publicWidget.registry.PropertyReport = publicWidget.Widget.extend({
    selector: "#wrap",
    events: {
        'change .type': '_onChangeType',
        'change .property_id': '_onChangeProperty',
        'click .add_total_property': '_onClickAddProperty',
        'click .remove_line': '_onClickRemoveLine',
        'click .custom_create': '_onClickSubmit',
        'change .start_date': '_calculateTotalDays',
        'change .end_date': '_calculateTotalDays',
    },
        start: function () {
        this._super.apply(this, arguments);
        const $firstRow = this.$('.property_order_line:first');
        this._fetchAndSetAmount($firstRow);
        return Promise.resolve();
      },


    _onChangeType: function (e) {
        this._fetchAndSetAmount($(e.currentTarget).closest('tr'));
    },

    _onChangeProperty: function (e) {
        this._fetchAndSetAmount($(e.currentTarget).closest('tr'));
    },

    _fetchAndSetAmount: function ($row) {
        const propertyId = $row.find('.property_id').val();
        const type = $('.type').val();  // assumed same for all rows

        if (!propertyId || !type) {
            console.warn("Both property and type must be selected.");
            return;
        }

        this.orm = this.bindService("orm");

        this.orm.call('property.management', 'get_property_amount', [propertyId, type])
            .then((amount) => {
                $row.find('.amount').val(amount);
                this._calculateRowTotal($row); // update total if dates already present
            })
            .catch((err) => {
                console.error("Error fetching amount:", err);
            });
    },

    _onClickAddProperty: function (e) {
        e.preventDefault();
        const $firstRow = $('#property_table tbody tr.property_order_line:first');
        const $newRow = $firstRow.clone();

        // Reset inputs
        $newRow.find('input, select').val('');
        $('#property_table tbody').append($newRow);
    },

    _onClickRemoveLine: function (e) {
        e.preventDefault();
        const $row = $(e.currentTarget).closest('tr');
        if ($('#property_table tbody tr').length > 1) {
            $row.remove();
        }
    },

    _onClickSubmit: function (e) {
        e.preventDefault();
        alert("Submit button clicked");
    },

    _calculateTotalDays: function (e) {
        const $row = $(e.currentTarget).closest('tr');
        this._calculateRowTotal($row);
    },

    _calculateRowTotal: function ($row) {
        const startDate = $('.start_date').val();
        const endDate = $('.end_date').val();
        const amount = parseFloat($row.find('.amount').val()) || 0;

        if (startDate && endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);

            const diffTime = end - start;
            const days = Math.ceil(diffTime / (1000 * 3600 * 24));

            if (days >= 0) {
                $row.find('.total_days').val(days);
                $row.find('.total_amount').val(days * amount);
            } else {
                alert("End date must be after Start date.");
                $row.find('.total_days, .total_amount').val('');
            }
        }
    }
});
