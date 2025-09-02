/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SaleDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({ total_quotation: 0, total_sale_order: 0, total_revenue: 0, customers: [] });
        onMounted(() => {
            this.renderChart();
        });
        this.loadData();
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
      const sales_team_result = await this.orm.call('sale.order','get_sales_team',[],{})
      console.log(sales_team_result)
      const sales_team_data = sales_team_result;
      const sales_team_labels = sales_team_data.map(order => order.team_name);
      const sales_team_name = sales_team_labels.map(team => team.en_US);
      const values = sales_team_data.map(order => order.total_orders);
      console.log(sales_team_name)
      console.log(sales_team_labels)
      const sales_person_result = await this.orm.call('sale.order','get_sales_person',[],{})
      console.log(sales_person_result)
      const sales_person_values = sales_person_result.map(order => order.total_orders);
      const sales_person_labels = sales_person_result.map(order => order.user_name);
      console.log(sales_person_labels)

      const sales_team = document.getElementById("dashboard_chart");
      if (sales_team) {
        new Chart(sales_team, {
            type: "line",
            data: {
                labels: sales_team_name,
                datasets: [{
                    backgroundColor: "black",
                    data: values
                }]
            },
            options: {
                    responsive: true,
                    legend: { display: false }
            }
        });
      }

      const sales_person = document.getElementById("dashboard_sales_chart");
      if (sales_person) {
        new Chart(sales_person, {
            type: "line",
            data: {
                labels: sales_person_labels,
                datasets: [{
                    backgroundColor: "black",
                    data: sales_person_values
                }]
            },
            options: {
                    responsive: true,
                    legend: { display: false }
            }
        });
      }

      const lowest_selling_product = document.getElementById("dashboard_lowest_product_chart");
      const lowest_selling_product_data = await this.orm.call('sale.order','get_lowest_selling_product',[],{})
      console.log('lowest:',lowest_selling_product_data);
      const lowest_selling_product_label = lowest_selling_product_data.map(product => product.name);
      const lowest_selling_product_value = lowest_selling_product_data.map(product => product.total);
      if (lowest_selling_product) {
        new Chart(lowest_selling_product, {
            type: "bar",
            data: {
                labels: lowest_selling_product_label,
                datasets: [{
                    backgroundColor: "black",
                    data: lowest_selling_product_value,

                }]
            },
            options: {
                    responsive: true,

                    legend: { display: false }
            }
        });
      }


//      const order_status = new Chart("dashboard_order_status_chart", {
//            type: "pie",
//            data: {
//                datasets: [{
//                    backgroundColor: "black",
//                    data: [0, 10, 20, 30, 40]
//                }]
//            },
//            options: {}
//      });
//      const invoice_status = new Chart("dashboard_invoice_status_chart", {
//            type: "pie",
//            data: {
//                datasets: [{
//                    backgroundColor: "black",
//                    data: [0, 10, 20, 30, 40]
//                }]
//            },
//            options: {}
//      });

//      const lowest_product = new Chart("dashboard_lowest_product_chart", {
//            type: "line",
//            data: {
//                labels: [10, 20, 30, 40, 50],
//                datasets: [{
//                    data: [10, 20, 30, 40, 50],
//                    pointBackgroundColor: "black",
//                }]
//            },
//            option: {}
//      });
    }


}
SaleDashboard.template = "sales_dashboard.SaleDashboard";
registry.category("actions").add("sale_dashboard_tag", SaleDashboard);


