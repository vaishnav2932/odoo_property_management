import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from '@web/core/network/rpc';

publicWidget.registry.PropertyReport = publicWidget.Widget.extend({
    selector: "#wrap",
    events: {
        'change .type': '_onChangeType',
        'change .property_id': '_onChangeProperty',
        'click .add_total_property': '_onClickAddProperty',
        'click .remove_line': '_onClickRemoveLine',
//        'click .custom_create': '_onClickSubmit',
        'change .start_date': '_calculateTotalDays',
        'change .end_date': '_calculateTotalDays',
        'change .amount': '_rowAmountChange',
    },
        start: function () {
        this._super.apply(this, arguments);
        const $firstRow = this.$('.property_order_line:first');
        this._fetchAndSetAmount($firstRow);
        return Promise.resolve();
      },


    _onChangeType: function (e) {
        this._fetchAndSetAmount($(e.currentTarget).closest('tr'));
        this._calculateTotalAmount($(e.currentTarget).closest('tr'));
    },
    _onChangeType: function (e) {
    const $rows = this.$('.property_order_line'); // Select all rows
    $rows.each((index, row) => {
        this._fetchAndSetAmount($(row));
        this._calculateTotalAmount($(row));


// Call the amount fetching for each row
    });


   },

    _onChangeProperty: function (e) {
        this._fetchAndSetAmount($(e.currentTarget).closest('tr'));
        this._calculateTotalDays($(e.currentTarget).closest('tr'));
        this._calculateTotalAmount($(e.currentTarget).closest('tr'));

    },

//    _fetchAndSetAmount: function ($row) {
//        const propertyId = $row.find('.property_id').val();
//        const type = $('.type').val();  // assumed same for all rows
//
//        if (!propertyId || !type) {
//            console.warn("Both property and type must be selected.");
//            return;
//        }
//
//        this.orm = this.bindService("orm");
//
//        this.orm.call('property.management', 'get_property_amount', [propertyId, type])
//            .then((amount) => {
//                $row.find('.amount').val(amount);
////                this._calculateRowTotal($row); // update total if dates already present
//            })
//            .catch((err) => {
//                console.error("Error fetching amount:", err);
//            });
//    },
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

            // ✅ Trigger total days and amount calculation after setting amount
            this._calculateTotalDays({ currentTarget: $row.find('.start_date')[0] });
            this._calculateTotalAmount($row);
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

//    _onClickSubmit: function (e) {
//        e.preventDefault();
//        alert("Submit button clicked");
//    },

//    _calculateTotalDays: function (e) {
//    const $row = $(e.currentTarget).closest('tr');
//    console.log("Row found:", $row);
//
//    const startDate = $row.find('.start_date').val();
//    const endDate = $row.find('.end_date').val();
//
//    console.log("Start:", startDate, "End:", endDate);
//
//    if (!startDate || !endDate) return;
//
//    const start = new Date(startDate);
//    const end = new Date(endDate);
//    const diffTime = end - start;
//    const days = Math.ceil(diffTime / (1000 * 3600 * 24));
//
//    if (days >= 0) {
//        $row.find('.total_days').val(days);
//        const amount = parseFloat($row.find('.amount').val() || 0);
//        console.log("Amount:", amount, "Days:", days);
//
//        const totalAmount = days * amount;
//        $row.find('.row_total').val(!isNaN(totalAmount) ? totalAmount : '');
//    } else {
//        $row.find('.total_days').val('');
//        $row.find('.row_total').val('');
//    }
//  },

    _calculateTotalDays: function (e) {
        this._calculateTotalAmount($(e.currentTarget).closest('tr'));
        const $row = $(e.currentTarget).closest('tbody tr');
        console.log($row)
        const startDate = $('.start_date').val();
        const endDate = $('.end_date').val();
        const propAmount = $row.find('.amount').val();

        const prop = $row.find('.property_id')

        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = end - start;
        const days = Math.ceil(diffTime / (1000 * 3600 * 24));
        if (days >= 0) {
         this.$('.total_days').val(days);
        } else {
         this.$('.total_days').val('');
        }

    },
    _calculateTotalAmount: function ($row) {
        const amount = $row.find('.amount').val();
        const days = $row.find('.total_days').val();

        const totalAmount = days * amount
        if (amount && days){
        $row.find('.total_amount').val(totalAmount);

        }

    },

});