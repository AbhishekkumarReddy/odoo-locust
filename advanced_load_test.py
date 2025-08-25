import json
import random
import time
from locust import HttpUser, task, between, SequentialTaskSet

class BusinessProcessTest(SequentialTaskSet):
    """Simulate complete business processes"""

    def on_start(self):
        """Login before starting the sequence"""
        self.user.login()

    @task
    def create_customer_journey(self):
        """Complete customer creation to sale order process"""
        # Step 1: Create customer
        partner_data = {
            "name": f"Journey Customer {random.randint(1000, 9999)}",
            "email": f"journey{random.randint(1000, 9999)}@example.com",
            "is_company": True
        }

        partner_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.partner",
                "method": "create",
                "args": [partner_data],
                "kwargs": {}
            },
            "id": random.randint(1, 1000000)
        }

        partner_response = self.client.post("/web/dataset/call_kw/res.partner/create",
                                            json=partner_payload,
                                            name="Journey: Create Customer")

        try:
            partner_result = partner_response.json()
            partner_id = partner_result.get('result')

            if partner_id:
                time.sleep(2)  # Simulate user thinking time

                # Step 2: Create sale order for this customer
                order_data = {
                    "partner_id": partner_id,
                    "state": "draft"
                }

                order_payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "model": "sale.order",
                        "method": "create",
                        "args": [order_data],
                        "kwargs": {}
                    },
                    "id": random.randint(1, 1000000)
                }

                self.client.post("/web/dataset/call_kw/sale.order/create",
                                 json=order_payload,
                                 name="Journey: Create Sale Order")

        except Exception as e:
            print(f"Business process failed: {e}")


class ReportsUser(HttpUser):
    """User focused on reporting and analytics"""
    weight = 1
    wait_time = between(10, 30)

    def on_start(self):
        self.login()

    @task(5)
    def sales_analysis(self):
        """Heavy sales analysis queries"""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "sale.order",
                "method": "read_group",
                "args": [[]],
                "kwargs": {
                    "fields": ["amount_total:sum", "partner_id"],
                    "groupby": ["partner_id"],
                    "limit": 50
                }
            },
            "id": random.randint(1, 1000000)
        }

        self.client.post("/web/dataset/call_kw/sale.order/read_group",
                         json=payload,
                         name="Sales Analysis Report")

    @task(3)
    def inventory_analysis(self):
        """Inventory analysis queries"""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "stock.quant",
                "method": "read_group",
                "args": [[]],
                "kwargs": {
                    "fields": ["quantity:sum", "product_id"],
                    "groupby": ["product_id"],
                    "limit": 100
                }
            },
            "id": random.randint(1, 1000000)
        }

        self.client.post("/web/dataset/call_kw/stock.quant/read_group",
                         json=payload,
                         name="Inventory Analysis Report")

