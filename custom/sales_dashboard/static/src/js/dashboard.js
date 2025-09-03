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
   action_quotation() {
    this.action.doAction({
        type: 'ir.actions.act_window',
        name: 'Quotations',
        res_model: 'sale.order',
        views: [[false, 'list'], [false, 'form']],
        domain: [["state", "in", ["sent"]]],  // quotations only
        target: 'current',
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

    async renderChart() {
//    sales team chart
      const sales_team_result = await this.orm.call("sale.order", "get_sales_team", [], {});
      console.log("sales", sales_team_result);
      const sales_team_labels = sales_team_result.map(order => order.team_name);
      const sales_team_name = sales_team_labels.map(team => team.en_US);
      const count = sales_team_result.map(order => order.total_orders);
      const price = sales_team_result.map(order => order.total_amount);
        console.log("price:", price);
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

//sales person chart
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
      const lowest_selling_product_data = await this.orm.call('sale.order','get_lowest_selling_product',[],{})
      console.log('lowest:',lowest_selling_product_data);
      const lowest_selling_product_label = lowest_selling_product_data.map(product => product.name);
      const lowest_selling_product_value = lowest_selling_product_data.map(product => product.total);
      const lowest_selling_product = document.getElementById("dashboard_lowest_product_chart");
            if (lowest_selling_product) {
        new Chart(lowest_selling_product, {
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
      const highest_selling_product_data = await this.orm.call('sale.order','get_highest_selling_product', [],{})
      const highest_selling_product_label = highest_selling_product_data.map(product => product.name);
      const highest_selling_product_value = highest_selling_product_data.map(product => product.total);
      const highest_selling_product = document.getElementById("dashboard_highest_product_chart");
            if (highest_selling_product) {
        new Chart(highest_selling_product, {
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
      const order_status_data = await this.orm.call('sale.order','get_order_status', [], {});
      console.log('order_status',order_status_data)
      const order_status_value = order_status_data.map(status => status.state_count);
      const order_status_labels = order_status_data.map(status => status.state);
      const order_status = document.getElementById("dashboard_order_status_chart");
            if (order_status) {
        new Chart(order_status, {
            type: "pie",
            data: {
                labels: order_status_labels,
                datasets: [{
                    backgroundColor: PIE_CHART_COLORS.slice(0, this.state.order_status_data),
                    data: order_status_value,
                }]
            },
            options: {
                    responsive: true,
                    legend: { display: false }
            }
        });
      }

//      invoice status chart
       const invoice_status_data = await this.orm.call('sale.order', 'get_invoice_status', [],{});
       const invoice_status_label = invoice_status_data.map(status => status.invoice_status);
       const invoice_status_value = invoice_status_data.map(status => status.count);
       const invoice_status = document.getElementById("dashboard_invoice_status_chart");
                if (invoice_status) {
            new Chart(invoice_status, {
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
                        legend: { display: false }
                }
            });
       }
    }
}
SaleDashboard.template = "sales_dashboard.SaleDashboard";
registry.category("actions").add("sale_dashboard_tag", SaleDashboard);