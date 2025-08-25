import json
import random
from faker import Faker

fake = Faker()

class TestDataGenerator:
    """Generate realistic test data for Odoo load testing"""

    @staticmethod
    def generate_partners(count=100):
        """Generate partner data"""
        partners = []
        for i in range(count):
            is_company = random.choice([True, False])

            partner = {
                "name": fake.company() if is_company else fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "is_company": is_company,
                "street": fake.street_address(),
                "city": fake.city(),
                "zip": fake.zipcode(),
                "country_id": random.randint(1, 50),  # Adjust based on your countries
                "category_id": [[6, 0, [random.randint(1, 10)]]]  # Random categories
            }

            if is_company:
                partner["website"] = fake.url()

            partners.append(partner)

        return partners

    @staticmethod
    def generate_products(count=50):
        """Generate product data"""
        products = []
        categories = [
            "Electronics", "Clothing", "Food", "Books", "Home & Garden",
            "Sports", "Automotive", "Health", "Beauty", "Toys"
        ]

        for i in range(count):
            product = {
                "name": f"{fake.word().title()} {fake.word().title()}",
                "list_price": round(random.uniform(5.0, 500.0), 2),
                "standard_price": round(random.uniform(3.0, 300.0), 2),
                "type": random.choice(["product", "service", "consu"]),
                "categ_id": random.randint(1, 20),  # Adjust based on your categories
                "active": True,
                "description": fake.text(max_nb_chars=200),
                "weight": round(random.uniform(0.1, 10.0), 2),
                "volume": round(random.uniform(0.01, 1.0), 3)
            }
            products.append(product)

        return products

    @staticmethod
    def save_test_data():
        """Save generated test data to files"""
        partners = TestDataGenerator.generate_partners(100)
        products = TestDataGenerator.generate_products(50)

        with open('test_partners.json', 'w') as f:
            json.dump(partners, f, indent=2)

        with open('test_products.json', 'w') as f:
            json.dump(products, f, indent=2)

        print("Test data generated and saved to files")
