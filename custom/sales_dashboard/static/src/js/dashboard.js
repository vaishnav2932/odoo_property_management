/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SaleDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({ total_quotation: 0, total_sale_order: 0, total_revenue: 0 });
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
            console.log(sales_team_data)

        } catch (err) {
            console.error("Error fetching quotations:", err);
        }
    }

    async renderChart() {
      const sales_team = document.getElementById("dashboard_chart");
      const sales_team_result = await this.orm.call('sale.order','get_sales_team',[],{})


    const sales_team_data = sales_team_result.sales_team || [];
    const labels = sales_team_data.map(team => team.name);
    const values = sales_team_data.map(team => team.sale_order_count);

      if (sales_team) {
        new Chart(sales_team, {
            type: "bar",
            data: {
                labels: labels,
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
            type: "bar",
            data: {
                labels: ["bar1", "bar2", "bar3", "bar4"],
                datasets: [{
                    backgroundColor: "black",
                    data: [0, 10, 20, 30]
                }]
            },
            options: {
                    responsive: true,
                    legend: { display: false }
            }
        });
      }

      const top_customer = document.getElementById("dashboard_customers_chart");
      if (top_customer) {
        new Chart(top_customer, {
            type: "bar",
            data: {
                labels: ["bar1", "bar2", "bar3", "bar4"],
                datasets: [{
                    backgroundColor: "black",
                    data: [0, 10, 20, 30],

                }]
            },
            options: {
                    responsive: true,
                    indexAxis: 'y',
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


