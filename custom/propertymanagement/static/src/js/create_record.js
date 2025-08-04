import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from '@web/core/network/rpc';

publicWidget.registry.PropertyReport = publicWidget.Widget.extend({
    selector: "#wrap",
    events: {
        'change .type': '_onChangeType',
        'change .property_id': '_onChangeProperty',
        'change .start_date': '_calculateTotalDays',
        'change .end_date': '_calculateTotalDays',
        'change .total_days': '_calculateTotalAmount',
        'click .add_total_property': '_onClickAddProperty',
        'click .remove_line': '_onClickRemoveLine',

    },
        start: function () {
        this._super.apply(this, arguments);
        const $firstRow = this.$('.property_order_line:first');
        this._fetchAndSetAmount($firstRow);
        return Promise.resolve();
      },



    _onChangeType: function (e) {
    const $rows = this.$('.property_order_line');
    $rows.each((index, row) => {
        this._fetchAndSetAmount($(row));
        this._calculateTotalAmount($(row));
    });

   },
    _onChangeProperty: function (e) {
        this._fetchAndSetAmount($(e.currentTarget).closest('tr'));
        this._calculateTotalDays($(e.currentTarget).closest('tr'));
        this._calculateTotalAmount($(e.currentTarget).closest('tr'));
        this._calculateTableTotal();

    },

    _fetchAndSetAmount: function ($row) {
    const propertyId = $row.find('.property_id').val();
    const type = $('.type').val();
    if (!propertyId || !type) {
        console.warn("Both property and type must be selected.");
        return;
    }
    this.orm = this.bindService("orm");
    this.orm.call('property.management', 'get_property_amount', [propertyId, type])
        .then((amount) => {
            $row.find('.amount').val(amount);
            this._calculateTotalDays({ currentTarget: $row.find('.start_date')[0] });
            this._calculateTotalAmount($row);
            this._calculateTableTotal();
        })
        .catch((err) => {
            console.error("Error fetching amount:", err);
        });
    },

    _onClickAddProperty: function (e) {
        e.preventDefault();
        const $firstRow = $('#property_table tbody tr.property_order_line:first');
        const $newRow = $firstRow.clone();
        $newRow.find('input, select').val('');
        $('#property_table tbody').append($newRow);
    },

    _onClickRemoveLine: function (e) {
        e.preventDefault();
        const $row = $(e.currentTarget).closest('tr');
        if ($('#property_table tbody tr').length > 1) {
            $row.remove();
        }
        this._calculateTableTotal();
    },

    _calculateTotalDays: function (e) {
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
        const $rows = this.$('.property_order_line');
        $rows.each((index, row) => {
           this._calculateTotalAmount($(row));
        });

    },


    _calculateTotalAmount: function ($row) {
    const amountStr = $row.find('.amount').val();
    const daysStr = $row.find('.total_days').val();
    const amount = parseFloat(amountStr) || 0;
    const days = parseFloat(daysStr) || 0;
    const totalAmount = days * amount;
    if (!isNaN(totalAmount)) {
        $row.find('.total_amount').val(totalAmount.toFixed(2));
    } else {
        $row.find('.total_amount').val('');
    }
    this._calculateTableTotal();
 },

    _calculateTableTotal: function () {
    let total =0
    $('#property_table .total_amount').each(function() {
       const value = parseFloat($(this).val());
       if (!isNaN(value)) {
           total += value;
       console.log(total)
      }
    });
    this.$('#table_total').val(total.toFixed(2));
    },

});