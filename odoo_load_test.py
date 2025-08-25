import json
import random
import time
from locust import HttpUser, task, between
from urllib.parse import urlencode
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OdooLoadTest(HttpUser):
    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csrf_token = None
        self.session_id = None
        self.database = "medunited_acc_prod_latest"  # Change this
        self.user_id = None

    def on_start(self):
        """Initialize session and login"""
        self.login()

    def get_csrf_token(self):
        """Extract CSRF token from login page"""
        try:
            response = self.client.get("/web/login", name="Get Login Page")
            if 'csrf_token' in response.text:
                start = response.text.find('csrf_token') + len('csrf_token":"')
                end = response.text.find('"', start)
                self.csrf_token = response.text[start:end]
                logger.info(f"CSRF token obtained: {self.csrf_token[:20]}...")
        except Exception as e:
            logger.error(f"Failed to get CSRF token: {e}")

    def login(self):
        """Login to Odoo system"""
        self.get_csrf_token()

        login_data = {
            "login": "abhishek.y",  # Change to your test user
            "password": "9#tpSOxG9^qII#",  # Change to your test password
            "csrf_token": self.csrf_token,
            "redirect": ""
        }

        with self.client.post("/web/login",
                              data=login_data,
                              name="Login",
                              catch_response=True) as response:
            if response.status_code == 200 and "/web" in response.url:
                logger.info("Login successful")
                # Extract session info if needed
                self.extract_session_info()
            else:
                logger.error(f"Login failed: {response.status_code}")
                response.failure(f"Login failed with status {response.status_code}")

    def extract_session_info(self):
        """Extract session information for API calls"""
        try:
            response = self.client.get("/web", name="Get Web Interface")
            if "session_info" in response.text:
                # Extract user_id and other session data
                start = response.text.find('"uid":') + len('"uid":')
                end = response.text.find(',', start)
                self.user_id = int(response.text[start:end])
                logger.info(f"User ID extracted: {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to extract session info: {e}")

    # =============================================================================
    # MENU LOADING TESTS
    # =============================================================================

    @task(10)
    def load_main_dashboard(self):
        """Load main dashboard/home page"""
        with self.client.get("/web", name="Main Dashboard") as response:
            if response.status_code != 200:
                response.failure("Dashboard failed to load")

    @task(8)
    def load_sales_menu(self):
        """Load Sales menu and views"""
        menu_params = {
            "action": "sale.action_orders",
            "model": "sale.order",
            "view_type": "list",
            "menu_id": "174"  # Adjust based on your menu structure
        }

        url = f"/web#{urlencode(menu_params)}"
        with self.client.get(url, name="Sales Menu") as response:
            if response.status_code != 200:
                response.failure("Sales menu failed to load")

    @task(6)
    def load_inventory_menu(self):
        """Load Inventory menu"""
        menu_params = {
            "action": "stock.action_picking_tree_all",
            "model": "stock.picking",
            "view_type": "list"
        }

        url = f"/web#{urlencode(menu_params)}"
        with self.client.get(url, name="Inventory Menu") as response:
            if response.status_code != 200:
                response.failure("Inventory menu failed to load")

    @task(5)
    def load_accounting_menu(self):
        """Load Accounting menu"""
        menu_params = {
            "action": "account.action_move_journal_line",
            "model": "account.move",
            "view_type": "list"
        }

        url = f"/web#{urlencode(menu_params)}"
        with self.client.get(url, name="Accounting Menu") as response:
            if response.status_code != 200:
                response.failure("Accounting menu failed to load")

    # =============================================================================
    # DATA FETCHING TESTS
    # =============================================================================

    @task(15)
    def fetch_partners_data(self):
        """Fetch partners/customers data"""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.partner",
                "method": "search_read",
                "args": [[]],
                "kwargs": {
                    "fields": ["name", "email", "phone", "is_company"],
                    "limit": 50,
                    "offset": random.randint(0, 100)
                }
            },
            "id": random.randint(1, 1000000)
        }

        with self.client.post("/web/dataset/call_kw/res.partner/search_read",
                              json=payload,
                              name="Fetch Partners Data") as response:
            if response.status_code != 200:
                response.failure("Failed to fetch partners data")

    @task(12)
    def fetch_products_data(self):
        """Fetch products data"""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "product.template",
                "method": "search_read",
                "args": [[]],
                "kwargs": {
                    "fields": ["name", "list_price", "categ_id", "active"],
                    "limit": 50,
                    "offset": random.randint(0, 50)
                }
            },
            "id": random.randint(1, 1000000)
        }

        with self.client.post("/web/dataset/call_kw/product.template/search_read",
                              json=payload,
                              name="Fetch Products Data") as response:
            if response.status_code != 200:
                response.failure("Failed to fetch products data")

    @task(10)
    def fetch_sales_orders(self):
        """Fetch sales orders data"""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "sale.order",
                "method": "search_read",
                "args": [[]],
                "kwargs": {
                    "fields": ["name", "partner_id", "amount_total", "state", "date_order"],
                    "limit": 30,
                    "order": "date_order desc"
                }
            },
            "id": random.randint(1, 1000000)
        }

        with self.client.post("/web/dataset/call_kw/sale.order/search_read",
                              json=payload,
                              name="Fetch Sales Orders") as response:
            if response.status_code != 200:
                response.failure("Failed to fetch sales orders")

    # =============================================================================
    # CREATION APIs TESTS
    # =============================================================================

    @task(5)
    def create_partner(self):
        """Create a new partner/customer"""
        partner_data = {
            "name": f"Test Customer {random.randint(1000, 9999)}",
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "phone": f"+1-555-{random.randint(1000, 9999)}",
            "is_company": random.choice([True, False]),
            "street": f"{random.randint(100, 999)} Test Street",
            "city": "Test City",
            "zip": f"{random.randint(10000, 99999)}"
        }

        payload = {
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

        with self.client.post("/web/dataset/call_kw/res.partner/create",
                              json=payload,
                              name="Create Partner") as response:
            if response.status_code != 200:
                response.failure("Failed to create partner")
            else:
                try:
                    result = response.json()
                    if 'error' in result:
                        response.failure(f"Partner creation error: {result['error']}")
                    else:
                        logger.info(f"Partner created with ID: {result.get('result')}")
                except:
                    response.failure("Invalid JSON response for partner creation")

    @task(3)
    def create_product(self):
        """Create a new product"""
        product_data = {
            "name": f"Test Product {random.randint(1000, 9999)}",
            "list_price": round(random.uniform(10.0, 1000.0), 2),
            "type": random.choice(["product", "service"]),
            "categ_id": 1,  # All / Saleable category - adjust as needed
            "active": True,
            "description": f"Test product description {random.randint(1, 100)}"
        }

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "product.template",
                "method": "create",
                "args": [product_data],
                "kwargs": {}
            },
            "id": random.randint(1, 1000000)
        }

        with self.client.post("/web/dataset/call_kw/product.template/create",
                              json=payload,
                              name="Create Product") as response:
            if response.status_code != 200:
                response.failure("Failed to create product")
            else:
                try:
                    result = response.json()
                    if 'error' in result:
                        response.failure(f"Product creation error: {result['error']}")
                    else:
                        logger.info(f"Product created with ID: {result.get('result')}")
                except:
                    response.failure("Invalid JSON response for product creation")

    @task(2)
    def create_sale_order(self):
        """Create a new sales order"""
        # First, get a random partner ID
        partner_search_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.partner",
                "method": "search",
                "args": [[]],
                "kwargs": {"limit": 1, "offset": random.randint(0, 10)}
            },
            "id": random.randint(1, 1000000)
        }

        partner_response = self.client.post("/web/dataset/call_kw/res.partner/search",
                                            json=partner_search_payload)

        try:
            partner_result = partner_response.json()
            partner_id = partner_result.get('result', [1])[0] if partner_result.get('result') else 1
        except:
            partner_id = 1  # Fallback to admin user

        # Create the sales order
        order_data = {
            "partner_id": partner_id,
            "state": "draft",
            "date_order": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        payload = {
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

        with self.client.post("/web/dataset/call_kw/sale.order/create",
                              json=payload,
                              name="Create Sale Order") as response:
            if response.status_code != 200:
                response.failure("Failed to create sale order")
            else:
                try:
                    result = response.json()
                    if 'error' in result:
                        response.failure(f"Sale order creation error: {result['error']}")
                    else:
                        logger.info(f"Sale order created with ID: {result.get('result')}")
                except:
                    response.failure("Invalid JSON response for sale order creation")

    # =============================================================================
    # UPDATE/WRITE OPERATIONS
    # =============================================================================

    @task(4)
    def update_partner(self):
        """Update an existing partner"""
        # First search for a partner to update
        search_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.partner",
                "method": "search",
                "args": [[]],
                "kwargs": {"limit": 1, "offset": random.randint(0, 20)}
            },
            "id": random.randint(1, 1000000)
        }

        search_response = self.client.post("/web/dataset/call_kw/res.partner/search",
                                           json=search_payload)

        try:
            search_result = search_response.json()
            partner_ids = search_result.get('result', [])

            if partner_ids:
                partner_id = partner_ids[0]

                # Update the partner
                update_data = {
                    "phone": f"+1-555-{random.randint(1000, 9999)}",
                    "street": f"{random.randint(100, 999)} Updated Street"
                }

                update_payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "model": "res.partner",
                        "method": "write",
                        "args": [[partner_id], update_data],
                        "kwargs": {}
                    },
                    "id": random.randint(1, 1000000)
                }

                with self.client.post("/web/dataset/call_kw/res.partner/write",
                                      json=update_payload,
                                      name="Update Partner") as response:
                    if response.status_code != 200:
                        response.failure("Failed to update partner")
        except Exception as e:
            logger.error(f"Error in update_partner: {e}")

    # =============================================================================
    # SEARCH AND FILTER OPERATIONS
    # =============================================================================

    @task(8)
    def search_with_filters(self):
        """Test search with various filters"""
        search_domains = [
            [['is_company', '=', True]],  # Companies only
            [['email', '!=', False]],     # Partners with email
            [['active', '=', True]],      # Active partners only
            [['create_date', '>=', '2023-01-01']]  # Recent partners
        ]

        domain = random.choice(search_domains)

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.partner",
                "method": "search_read",
                "args": [domain],
                "kwargs": {
                    "fields": ["name", "email", "is_company"],
                    "limit": 20
                }
            },
            "id": random.randint(1, 1000000)
        }

        with self.client.post("/web/dataset/call_kw/res.partner/search_read",
                              json=payload,
                              name="Search with Filters") as response:
            if response.status_code != 200:
                response.failure("Failed to search with filters")

    # =============================================================================
    # REPORTING AND HEAVY OPERATIONS
    # =============================================================================

    @task(2)
    def generate_report(self):
        """Test report generation (lighter version)"""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "sale.order",
                "method": "search_count",
                "args": [[]],
                "kwargs": {}
            },
            "id": random.randint(1, 1000000)
        }

        with self.client.post("/web/dataset/call_kw/sale.order/search_count",
                              json=payload,
                              name="Generate Report Count") as response:
            if response.status_code != 200:
                response.failure("Failed to generate report")


# =============================================================================
# DIFFERENT USER BEHAVIOR PATTERNS
# =============================================================================

class HeavyUser(OdooLoadTest):
    """Simulates users doing heavy operations"""
    weight = 1

    @task(20)
    def heavy_data_operations(self):
        """Perform heavy data operations"""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "res.partner",
                "method": "search_read",
                "args": [[]],
                "kwargs": {
                    "fields": ["name", "email", "phone", "street", "city", "country_id"],
                    "limit": 200  # Heavy load
                }
            },
            "id": random.randint(1, 1000000)
        }

        with self.client.post("/web/dataset/call_kw/res.partner/search_read",
                              json=payload,
                              name="Heavy Data Load") as response:
            if response.status_code != 200:
                response.failure("Heavy data operation failed")


class LightUser(OdooLoadTest):
    """Simulates casual users with light operations"""
    weight = 3
    wait_time = between(5, 15)  # Longer wait times

    @task
    def browse_menus(self):
        """Light browsing operations"""
        self.load_main_dashboard()
        time.sleep(2)
        self.load_sales_menu()


# =============================================================================
# CONFIGURATION
# =============================================================================

# To run this test:
# 1. Install locust: pip install locust
# 2. Update the configuration variables at the top of OdooLoadTest class
# 3. Run: locust -f this_file.py --host=https://your-odoo-domain.com
# 4. Open http://localhost:8089 to configure and start the test

# Example command line usage:
# locust -f odoo_load_test.py --host=https://your-odoo-domain.com -u 50 -r 5 -t 300s
# This runs 50 users, spawning 5 per second, for 300 seconds
