"""
Test script for Stripe payment integration

This script demonstrates how to test the FastAPI Stripe payment integration
with sample data. Use Stripe test card numbers for testing.

Stripe Test Card Numbers:
- Success: 4242 4242 4242 4242
- Decline: 4000 0000 0000 0002
- Requires Authentication: 4000 0025 0000 3155
- Any future expiry date and any 3-digit CVC
"""

import httpx
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30


class StripePaymentTester:
    """Helper class for testing Stripe payment integration"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(timeout=TEST_TIMEOUT)
        self.customers = []
        self.payments = []
    
    def health_check(self) -> dict:
        """Check if the API is running"""
        response = self.client.get(f"{self.base_url}/")
        return response.json()
    
    def create_customer(self, email: str, name: str, description: str = None) -> dict:
        """Create a test customer"""
        payload = {
            "email": email,
            "name": name,
            "description": description or f"Test customer for {email}"
        }
        response = self.client.post(
            f"{self.base_url}/customers/create",
            json=payload
        )
        if response.status_code == 200:
            customer = response.json()
            self.customers.append(customer)
            return customer
        else:
            print(f"Error creating customer: {response.text}")
            return None
    
    def create_payment(
        self,
        amount: int,
        description: str,
        customer_email: str,
        customer_name: str,
        payment_method_id: Optional[str] = None
    ) -> dict:
        """Create a test payment"""
        payload = {
            "amount": amount,
            "description": description,
            "customer_email": customer_email,
            "customer_name": customer_name,
            "currency": "usd"
        }
        
        if payment_method_id:
            payload["payment_method_id"] = payment_method_id
        
        response = self.client.post(
            f"{self.base_url}/payments/create",
            json=payload
        )
        if response.status_code == 200:
            payment = response.json()
            self.payments.append(payment)
            return payment
        else:
            print(f"Error creating payment: {response.text}")
            return None
    
    def confirm_payment(self, payment_id: str) -> dict:
        """Confirm a payment"""
        response = self.client.post(
            f"{self.base_url}/payments/{payment_id}/confirm"
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error confirming payment: {response.text}")
            return None
    
    def get_payment_status(self, payment_id: str) -> dict:
        """Get payment status"""
        response = self.client.get(
            f"{self.base_url}/payments/{payment_id}"
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting payment status: {response.text}")
            return None
    
    def refund_payment(self, payment_id: str, reason: str = None) -> dict:
        """Refund a payment"""
        payload = {
            "payment_id": payment_id,
            "reason": reason or "requested_by_customer"
        }
        response = self.client.post(
            f"{self.base_url}/payments/{payment_id}/refund",
            json=payload
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error refunding payment: {response.text}")
            return None
    
    def list_payment_methods(self, customer_id: str) -> list:
        """List payment methods for a customer"""
        response = self.client.get(
            f"{self.base_url}/customers/{customer_id}/payment-methods"
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error listing payment methods: {response.text}")
            return []
    
    def add_payment_method(self, customer_id: str, card_number: str, exp_month: int, 
                          exp_year: int, cvc: str, billing_name: str = None) -> dict:
        """Add a credit card payment method to a customer"""
        payload = {
            "card_number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc,
            "billing_name": billing_name or "Test Cardholder"
        }
        response = self.client.post(
            f"{self.base_url}/customers/{customer_id}/payment-methods",
            json=payload
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error adding payment method: {response.text}")
            return None
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()


# Sample test data
SAMPLE_CUSTOMERS = [
    {
        "email": "john.doe@example.com",
        "name": "John Doe",
        "description": "Premium customer"
    },
    {
        "email": "jane.smith@example.com",
        "name": "Jane Smith",
        "description": "Regular customer"
    },
    {
        "email": "bob.johnson@example.com",
        "name": "Bob Johnson",
        "description": "VIP customer"
    }
]

SAMPLE_PAYMENTS = [
    {
        "amount": 5000,  # $50.00
        "description": "Software license subscription",
        "currency": "usd"
    },
    {
        "amount": 12500,  # $125.00
        "description": "Premium support package",
        "currency": "usd"
    },
    {
        "amount": 99900,  # $999.00
        "description": "Enterprise license",
        "currency": "usd"
    },
    {
        "amount": 1000,  # $10.00
        "description": "Test transaction",
        "currency": "usd"
    }
]


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(operation: str, data: dict):
    """Print formatted operation results"""
    print(f"✓ {operation}")
    print(json.dumps(data, indent=2))
    print()


async def run_test_suite():
    """Run comprehensive test suite"""
    tester = StripePaymentTester()
    
    try:
        # Health check
        print_section("1. HEALTH CHECK")
        health = tester.health_check()
        print_result("API Health Check", health)
        
        # Create customers
        print_section("2. CREATE CUSTOMERS")
        created_customers = []
        for customer_data in SAMPLE_CUSTOMERS:
            customer = tester.create_customer(
                email=customer_data["email"],
                name=customer_data["name"],
                description=customer_data["description"]
            )
            if customer:
                print_result(f"Created Customer: {customer_data['name']}", customer)
                created_customers.append(customer)
        
        if not created_customers:
            print("⚠ No customers created. Make sure Stripe keys are configured correctly.")
            return
        
        # Create payments
        print_section("3. CREATE PAYMENTS")
        created_payments = []
        for i, payment_data in enumerate(SAMPLE_PAYMENTS):
            if i < len(created_customers):
                customer = created_customers[i]
                payment = tester.create_payment(
                    amount=payment_data["amount"],
                    description=payment_data["description"],
                    customer_email=customer["email"],
                    customer_name=customer["name"]
                )
                if payment:
                    print_result(f"Created Payment: {payment_data['description']}", payment)
                    created_payments.append(payment)
        
        # Get payment status
        print_section("4. CHECK PAYMENT STATUS")
        for payment in created_payments[:2]:  # Check first 2 payments
            status = tester.get_payment_status(payment["payment_id"])
            if status:
                print_result(f"Payment Status: {payment['payment_id']}", status)
        
        # List payment methods
        print_section("5. LIST PAYMENT METHODS")
        for customer in created_customers[:1]:  # List methods for first customer
            methods = tester.list_payment_methods(customer["customer_id"])
            print_result(f"Payment Methods for {customer['name']}", 
                        {"customer_id": customer["customer_id"], "methods": methods})
        
        # Add credit card payment methods
        print_section("5A. ADD CREDIT CARD PAYMENT METHOD")
        added_payment_methods = []
        
        # Test card data - use Stripe test card numbers
        test_cards = [
            {
                "number": "4242424242424242",  # Success card
                "exp_month": 12,
                "exp_year": 2025,
                "cvc": "123",
                "name": "Test Visa Card"
            },
            {
                "number": "5555555555554444",  # Mastercard test card
                "exp_month": 6,
                "exp_year": 2026,
                "cvc": "456",
                "name": "Test Mastercard"
            }
        ]
        
        for i, customer in enumerate(created_customers[:2]):  # Add card to first 2 customers
            if i < len(test_cards):
                card = test_cards[i]
                payment_method = tester.add_payment_method(
                    customer_id=customer["customer_id"],
                    card_number=card["number"],
                    exp_month=card["exp_month"],
                    exp_year=card["exp_year"],
                    cvc=card["cvc"],
                    billing_name=card["name"]
                )
                if payment_method:
                    print_result(f"Added {card['name']} for {customer['name']}", payment_method)
                    added_payment_methods.append(payment_method)
        
        # Verify payment methods were added
        print_section("5B. VERIFY SAVED PAYMENT METHODS")
        for customer in created_customers[:2]:
            methods = tester.list_payment_methods(customer["customer_id"])
            if methods:
                print_result(f"Saved Payment Methods for {customer['name']}", 
                            {"customer_id": customer["customer_id"], "methods_count": len(methods), "methods": methods})
        
        # Test Refund
        print_section("6. TEST REFUND (OPTIONAL)")
        if created_payments:
            payment = created_payments[0]
            print(f"Note: To test refund, the payment must be in 'succeeded' status.")
            print(f"Payment Status: {payment['status']}")
            print(f"Payment ID: {payment['payment_id']}")
            print("Once confirmed and succeeded, you can test refund with:")
            print(f"  refund = tester.refund_payment('{payment['payment_id']}', 'duplicate')")
        
        # Summary
        print_section("TEST SUMMARY")
        print(f"Total Customers Created: {len(created_customers)}")
        print(f"Total Payments Created: {len(created_payments)}")
        print(f"Total Payment Methods Added: {len(added_payment_methods)}")
        print("\nTest Stripe Keys Required:")
        print("  - STRIPE_SECRET_KEY (from https://dashboard.stripe.com/apikeys)")
        print("  - STRIPE_PUBLISHABLE_KEY (from https://dashboard.stripe.com/apikeys)")
        print("\nTest Card Numbers Added:")
        print("  - Visa: 4242 4242 4242 4242 (expires 12/2025)")
        print("  - Mastercard: 5555 5555 5555 4444 (expires 06/2026)")
        print("\nOther Test Card Numbers (use in sandbox only):")
        print("  - Success: 4242 4242 4242 4242")
        print("  - Decline: 4000 0000 0000 0002")
        print("  - Auth Required: 4000 0025 0000 3155")
        print("  - Any future expiry and any 3-digit CVC")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        tester.close()


if __name__ == "__main__":
    import asyncio
    print("\n🚀 Starting Stripe Payment Integration Test Suite")
    asyncio.run(run_test_suite())
