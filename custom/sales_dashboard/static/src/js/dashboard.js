/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SaleDashboard extends Component {
    setup() {
        this.action = useService("action")
        this.orm = useService("orm");
        this.state = useState({ total_quotation: 0, total_sale_order: 0, total_revenue: 0, customers: [] });
        onMounted(() => {
            this.renderChart();
        });
        this.loadData();
    }
    ViewOrders(){
        this.action.doAction({
          type:'ir.actions.act_window',
          name:'Orders',
          res_model:"sale.order",
          views: [[false, "list"], [false, "form"]],
          target:'current'
        });
    }
    ViewQuotations(){
    this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Quotations',
            res_model: "sale.order",
            views: [[false, "list"], [false, "form"]],
            target: 'current',
            domain: [["state", "in", ["draft","sent"]]],
        });
    }

    async loadData() {
        try {

            const result = await this.orm.call("sale.order", "get_sale_order_data", [], {});
            this.state.total_quotation = result.total_quotation;
            this.state.total_sale_order = result.total_sale_order;
            this.state.total_revenue = result.total_revenue;
            console.log(result)
            const top_customer_list = await this.orm.call('sale.order','get_top_customer', [],{});
            this.state.customers = top_customer_list;
        } catch (err) {
            console.error("Error fetching quotations:", err);
            this.state.customers = [];
        }
    }
    async fetchSalesRange(){
        const fromInput = document.getElementById('from_date')
        const toInput = document.getElementById('to_date')

        const fromValue = fromInput.value;
        const toValue = toInput.value;

        console.log(fromValue)


    }

    async renderChart() {
//    sales team chart
//    sales team day sale
      const team_day_order = await this.orm.call('sale.order', 'get_team_day_order', [], {});
      console.log(team_day_order)
      const team_day_count = team_day_order.map(order => order.total_orders)
      const team_day_price = team_day_order.map(order => order.total_amount)
//      sale team month sale
      const team_month_order = await this.orm.call('sale.order','get_month_orders_by_team', [], {})
      console.log('month order',team_month_order)
      const team_month_order_count = team_month_order.map(order => order.total_orders)
      const team_month_order_price = team_month_order.map(order => order.total_amount)
//    sale team default sale
      const sales_team_result = await this.orm.call("sale.order", "get_sales_team", [], {});
      const sales_team_labels = sales_team_result.map(order => order.team_name);
      const sales_team_name = sales_team_labels.map(team => team.en_US);
      const count = sales_team_result.map(order => order.total_orders);
      const price = sales_team_result.map(order => order.total_amount);

        const sales_team = document.getElementById("dashboard_chart");
        let chartInstance = null;
        if (sales_team) {
        chartInstance = new Chart(sales_team, {
            type: "line",
            data: {
                labels: sales_team_name,
                datasets: [{
                    label: "By Count",
                    backgroundColor: "blue",
                    borderColor: "blue",
                    fill: false,
                    data: count,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true },
                },
            },
        });
        }

        const filterSelect = document.getElementById("sale_filter");
        if (filterSelect && chartInstance) {
            filterSelect.onchange = (e) => {
                chartInstance.data.datasets[0].label = e.target.value === "val1" ? "By Count" : "By Price";
                chartInstance.data.datasets[0].data = e.target.value === "val1" ? count : price;
                chartInstance.update();
            };
        }
//     sale person chart
//     sale person daily sale
      const sale_person_day_order = await this.orm.call('sale.order','get_sale_person_day_order' , [],{})
      const sale_person_day_order_count = sale_person_day_order.map(order => order.total_orders)
      const sale_person_day_order_price = sale_person_day_order.map(order => order.total_amount)
//    sale person monthly sale
      const sale_person_monthly_order = await this.orm.call('sale.order', 'get_sale_person_month_order', [],{})
      const sale_person_monthly_order_count = sale_person_monthly_order.map(order => order.total_orders)
      const sale_person_monthly_order_price = sale_person_monthly_order.map(order => order.total_amount)
//    sale person default sale
      const sales_person_result = await this.orm.call('sale.order','get_sales_person',[],{})
      console.log(sales_person_result)
      const sales_person_count = sales_person_result.map(order => order.total_orders);
      const sales_person_price = sales_person_result.map(order => order.total_amount);
      const sales_person_labels = sales_person_result.map(order => order.user_name);
      console.log(sales_person_labels)
      const sales_person = document.getElementById("dashboard_sales_chart");
      let personChart = null;
      if (sales_person) {
        personChart = new Chart(sales_person, {
            type: "line",
            data: {
                labels: sales_person_labels,
                datasets: [{
                    label: "By Count",
                    backgroundColor: "blue",
                    borderColor: "blue",
                    data: sales_person_count
                }]
            },
            options: {
                    responsive: true,
                    legend: { display: false }
            }
        });
      }
      const personFilter = document.getElementById("sale_person_filter");
        if (personFilter && personChart) {
            personFilter.onchange = (e) => {
                personChart.data.datasets[0].label = e.target.value === "val1" ? "By Count" : "By Price";
                personChart.data.datasets[0].data = e.target.value === "val1" ? sales_person_count : sales_person_price;
                personChart.update();
            };
        }

//      lowest selling product chart
//    lowest selling daily product
      const lowest_daily_selling_product = await this.orm.call('sale.order','get_lowest_daily_selling_product', [], {})
      const lowest_daily_selling_count = lowest_daily_selling_product.map(product => product.total_orders);
      const lowest_daily_selling_price = lowest_daily_selling_product.map(product => product.total);
      const lowest_daily_selling_label = lowest_daily_selling_product.map(product => product.name);
//    lowest selling monthly product
      const lowest_monthly_selling_product = await this.orm.call('sale.order','get_lowest_monthly_selling_product', [], {})
      console.log(lowest_monthly_selling_product)
      const lowest_monthly_selling_count = lowest_monthly_selling_product.map(product => product.total_orders);
      console.log(lowest_monthly_selling_count)
      const lowest_monthly_selling_price = lowest_monthly_selling_product.map(product => product.total);
      const lowest_monthly_selling_label = lowest_monthly_selling_product.map(product => product.name);
//      lowest selling default
      const lowest_selling_product_data = await this.orm.call('sale.order','get_lowest_selling_product',[],{})
      console.log('lowest:',lowest_selling_product_data);
      const lowest_selling_product_label = lowest_selling_product_data.map(product => product.name);
      const lowest_selling_product_value = lowest_selling_product_data.map(product => product.total);
      const lowest_selling_count = lowest_selling_product_data.map(product => product.total_orders);
      let lowestProductChart = null;
      const lowest_selling_product = document.getElementById("dashboard_lowest_product_chart");
            if (lowest_selling_product) {
       lowestProductChart =  new Chart(lowest_selling_product, {
            type: "bar",
            data: {
                labels: lowest_selling_product_label,
                datasets: [{
                    backgroundColor: "blue",
                    label: "product",
                    data: lowest_selling_product_value,
                }]
            },
            options: {
                    responsive: true,
                    legend: { display: false }
            }
        });
      }

//      highest selling product chart
//    highest daily selling product
      const highest_daily_selling_product = await this.orm.call('sale.order','get_highest_daily_selling_product', [], {});
      const highest_daily_selling_count = highest_daily_selling_product.map(product => product.total_orders);
      const highest_daily_selling_price = highest_daily_selling_product.map(product => product.total);
      const highest_daily_selling_labels = highest_daily_selling_product.map(product => product.name);
//    highest monthly selling product
      const highest_monthly_selling_product = await this.orm.call('sale.order','get_highest_monthly_selling_product', [], {});
      const highest_monthly_selling_count = highest_monthly_selling_product.map(product => product.total_orders);
      const highest_monthly_selling_price = highest_monthly_selling_product.map(product => product.total);
      const highest_monthly_selling_labels = highest_monthly_selling_product.map(product => product.name);
//      highest monthly selling default
      const highest_selling_product_data = await this.orm.call('sale.order','get_highest_selling_product', [],{});
      const highest_selling_product_label = highest_selling_product_data.map(product => product.name);
      const highest_selling_product_value = highest_selling_product_data.map(product => product.total);
      const highest_selling_product_price = highest_selling_product_data.map(product => product.total_orders);
      let highestProductChart = null;
      const highest_selling_product = document.getElementById("dashboard_highest_product_chart");
            if (highest_selling_product) {
      highestProductChart = new Chart(highest_selling_product, {
            type: "bar",
            data: {
                labels: highest_selling_product_label,
                datasets: [{
                    label: "product",
                    backgroundColor: "blue",
                    data: highest_selling_product_value,

                }]
            },
            options: {
                    responsive: true,
                    legend: { display: false }
            }
        });
      }
//pie chart colors
      const PIE_CHART_COLORS = [
        '#0074D9', // blue
        '#FF4136', // red
        '#FF851B', // orange
        '#7FDBFF', // light blue
        '#B10DC9', // purple
        '#AAAAAA', // gray
    ];

//       order status chart
//    order daily status
      const order_daily_status = await this.orm.call('sale.order','get_order_daily_status', [], {})
      console.log('daily_order',order_daily_status)
      const get_order_daily_count = order_daily_status.map(status => status.state_count)
      const get_order_daily_price = order_daily_status.map(status = > status.total_amount)
//      order monthly status
      const order_monthly_status = await this.orm.call('sale.order','get_order_monthly_status', [], {})
      const order_monthly_count = order_monthly_status.map(status => status.state_count);
      const order_monthly_price = order_monthly_status.map(status => status.total_amount);
      console.log(order_monthly_count)
//      order default status
      const order_status_data = await this.orm.call('sale.order','get_order_status', [], {});
      console.log('order_status',order_status_data)
      const order_status_value = order_status_data.map(status => status.state_count);
      const order_status_labels = order_status_data.map(status => status.state);
      const order_status_price = order_status_data.map(status => status.total_amount);

      let orderChart = null;
      const order_status = document.getElementById("dashboard_order_status_chart");
            if (order_status) {
        orderChart = new Chart(order_status, {
            type: "pie",
            data: {
                labels: order_status_labels,
                datasets: [{
                    backgroundColor: PIE_CHART_COLORS.slice(0, this.state.order_status_data),
                    data: order_status_value,
                    label: order_status_labels
                }]
            },
            options: {
                 responsive: true,
                 legend: { display: true },
                  plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                // Ensure you always use the chart's current labels
                                const label = orderChart.data.labels[tooltipItem.dataIndex];
                                const value = tooltipItem.formattedValue;
                                return `${label}: ${value}`;
                            }
                        }
                    }
                  }
            }
        });
      }
//      invoice status chart
//      invoice daily satus
       const invoice_daily_status = await this.orm.call('sale.order', 'get_invoice_daily_status', [],{});
       const invoice_daily_count = invoice_daily_status.map(status => status.count);
       const invoice_daily_price = invoice_daily_status.map(status => status.total_amount);
//     invoice monthly status
       const invoice_monthly_status = await this.orm.call('sale.order','get_invoice_monthly_status', [],{});
       const invoice_monthly_count = invoice_monthly_status.map(status => status.count);
       const invoice_monthly_price = invoice_monthly_status.map(status => status.total_amount);
//       invoice default price
       const invoice_status_data = await this.orm.call('sale.order', 'get_invoice_status', [],{});
       const invoice_status_label = invoice_status_data.map(status => status.invoice_status);
       const invoice_status_value = invoice_status_data.map(status => status.count);
       const invoice_status_price = invoice_status_data.map(status => status.total_amount)
       let invoiceChart = null;
       const invoice_status = document.getElementById("dashboard_invoice_status_chart");
                if (invoice_status) {
           invoiceChart = new Chart(invoice_status, {
                type: "pie",
                data: {
                    labels: invoice_status_label,
                    datasets: [{
                        backgroundColor: PIE_CHART_COLORS.slice(0, this.state.invoice_status_data),
                        data: invoice_status_value,
                    }]
                },
                options: {
                        responsive: true,
                        legend: { display: true }
                }
            });
       }

      const MainFilterSelect = document.getElementById('main_filter')
      console.log(MainFilterSelect)
      if (MainFilterSelect && chartInstance) {
         MainFilterSelect.onchange = (e) => {
           if (e.target.value === 'day_count'){
               chartInstance.data.labels = sales_team_name;
               chartInstance.data.datasets[0].data = team_day_count;
               chartInstance.data.datasets[0].label = 'Daily count';
               personChart.data.datasets[0].data = sale_person_day_order_count;
               personChart.data.datasets[0].label = 'Daily count';
               orderChart.data.datasets[0].data = get_order_daily_count;
               invoiceChart.data.datasets[0].data = invoice_daily_count;
               highestProductChart.data.datasets[0].data = highest_daily_selling_count;
               highestProductChart.data.labels = highest_daily_selling_labels;
               lowestProductChart.data.datasets[0].data = lowest_daily_selling_count;
               lowestProductChart.data.labels = lowest_daily_selling_label;

           }
           if (e.target.value === 'day_price'){
               chartInstance.data.labels = sales_team_name;
               chartInstance.data.datasets[0].data = team_day_price;
               chartInstance.data.datasets[0].label = 'Daily price';
               personChart.data.datasets[0].data = sale_person_day_order_price;
               personChart.data.datasets[0].label = 'Daily price';
               orderChart.data.datasets[0].data = get_order_daily_price;
               invoiceChart.data.datasets[0].data = invoice_daily_price;
               highestProductChart.data.datasets[0].data = highest_daily_selling_price;
               highestProductChart.data.labels = highest_daily_selling_labels;
               lowestProductChart.data.datasets[0].data = lowest_daily_selling_price;
               lowestProductChart.data.labels = lowest_daily_selling_label;

           }
           if (e.target.value === 'month_count'){
               chartInstance.data.labels = sales_team_name;
               chartInstance.data.datasets[0].data = team_month_order_count;
               chartInstance.data.datasets[0].label = 'Monthly count';
               personChart.data.datasets[0].data = sale_person_monthly_order_count;
               personChart.data.datasets[0].label = 'Monthly price';
               orderChart.data.datasets[0].data = order_monthly_count;
               invoiceChart.data.datasets[0].data = invoice_monthly_count;
               highestProductChart.data.datasets[0].data = highest_monthly_selling_count;
               highestProductChart.data.labels = highest_monthly_selling_labels;
               lowestProductChart.data.datasets[0].data = lowest_monthly_selling_count;
               lowestProductChart.data.labels = lowest_monthly_selling_label;
           }
           if (e.target.value === 'month_price'){
               chartInstance.data.labels = sales_team_name;
               chartInstance.data.datasets[0].data = team_month_order_price;
               chartInstance.data.datasets[0].label = 'Monthly price';
               personChart.data.datasets[0].data = sale_person_monthly_order_price;
               personChart.data.datasets[0].label = 'Monthly price';
               orderChart.data.datasets[0].data = order_monthly_price;
               invoiceChart.data.datasets[0].data = invoice_monthly_price;
               highestProductChart.data.datasets[0].data = highest_monthly_selling_price;
               highestProductChart.data.labels = highest_monthly_selling_labels;
               lowestProductChart.data.datasets[0].data = lowest_monthly_selling_price;
               lowestProductChart.data.labels = lowest_monthly_selling_label;
           }
           if (e.target.value === 'year_count'){
               chartInstance.data.labels = sales_team_name;
               chartInstance.data.datasets[0].data = count;
               chartInstance.data.datasets[0].label = 'Yearly count';
               personChart.data.datasets[0].data = sales_person_count;
               personChart.data.datasets[0].label = 'Yearly count';
               orderChart.data.datasets[0].data = order_status_value;
               invoiceChart.data.datasets[0].data = invoice_status_value;
               highestProductChart.data.datasets[0].data = highest_selling_product_price;
               highestProductChart.data.labels = highest_selling_product_label;
               lowestProductChart.data.labels = lowest_selling_product_label;
               lowestProductChart.data.datasets[0].data = lowest_selling_count;
           }
           if (e.target.value === 'year_price'){
               chartInstance.data.labels = sales_team_name;
               chartInstance.data.datasets[0].data = price;
               chartInstance.data.datasets[0].label = 'Yearly price';
               personChart.data.datasets[0].data = sales_person_price;
               personChart.data.datasets[0].label = 'Yearly price';
               orderChart.data.datasets[0].data = order_status_price;
               invoiceChart.data.datasets[0].data = invoice_status_price;
               highestProductChart.data.datasets[0].data = highest_selling_product_value;
               highestProductChart.data.labels = highest_selling_product_label;
               lowestProductChart.data.labels = lowest_selling_product_label;
               lowestProductChart.data.datasets[0].data = lowest_selling_product_value;
           }
            chartInstance.update();
            personChart.update();
            orderChart.update();
            invoiceChart.update();
            highestProductChart.update();
            lowestProductChart.update();
         }
      }

        document.getElementById("apply_date_range").addEventListener("click", async () => {
        const from_date = document.getElementById("from_date").value;
        const to_date = document.getElementById("to_date").value;
    if (!from_date || !to_date) {
        alert("Please select both dates");
        return;
    }

    try {
        // Example 1: Sales by Team
        const teamData = await this.orm.call(
            "sale.order",
            "get_team_custom_orders",
            [from_date, to_date]
        );
        console.log("Team Sales:", teamData);

        // team_name is already a string
        const labels = teamData.map(item => item.team_name);
        const counts = teamData.map(item => item.total_orders);

        // update chart
        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = counts;
        chartInstance.update();

    } catch (error) {
        console.error("Error fetching team sales:", error);
    }




   }


//    const products = await this.orm.call(
//        "sale.order",
//        "get_products_custom",
//        [from_date, to_date, "DESC"]
//    );
//    console.log("Products:", products);
}
SaleDashboard.template = "sales_dashboard.SaleDashboard";
registry.category("actions").add("sale_dashboard_tag", SaleDashboard);