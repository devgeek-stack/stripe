"""
Advanced usage examples for Stripe payment integration
"""

import asyncio
import httpx
from datetime import datetime


# Example 1: Create a one-time payment with email receipt
async def example_simple_payment():
    """Simple payment workflow"""
    async with httpx.AsyncClient() as client:
        # Create payment
        payment_data = {
            "amount": 2999,  # $29.99
            "description": "Monthly subscription",
            "customer_email": "customer@example.com",
            "customer_name": "John Doe"
        }
        
        response = await client.post(
            "http://localhost:8000/payments/create",
            json=payment_data
        )
        
        payment = response.json()
        print(f"Payment created: {payment['payment_id']}")
        print(f"Status: {payment['status']}")
        print(f"Client Secret: {payment['client_secret']}")
        
        return payment


# Example 2: Create a payment with saved card
async def example_saved_card_payment():
    """Payment with saved card (payment method)"""
    async with httpx.AsyncClient() as client:
        # First, create a customer
        customer_data = {
            "email": "premium@example.com",
            "name": "Premium Customer",
            "description": "VIP customer with saved card"
        }
        
        customer_response = await client.post(
            "http://localhost:8000/customers/create",
            json=customer_data
        )
        
        customer = customer_response.json()
        print(f"Customer created: {customer['customer_id']}")
        
        # In production, save a card to Stripe and get payment_method_id
        # For now, this is just a demonstration
        payment_data = {
            "amount": 5000,  # $50.00
            "description": "Premium subscription renewal",
            "customer_email": customer["email"],
            "customer_name": customer["name"],
            "payment_method_id": "pm_1234567890"  # Replace with real payment method ID
        }
        
        payment_response = await client.post(
            "http://localhost:8000/payments/create",
            json=payment_data
        )
        
        payment = payment_response.json()
        print(f"Payment with saved card: {payment['payment_id']}")
        
        return payment


# Example 3: Bulk payment processing
async def example_bulk_payments():
    """Process multiple payments"""
    async with httpx.AsyncClient() as client:
        customers = [
            {"email": "user1@example.com", "name": "User One"},
            {"email": "user2@example.com", "name": "User Two"},
            {"email": "user3@example.com", "name": "User Three"},
        ]
        
        payments = []
        
        for customer in customers:
            payment_data = {
                "amount": 1000,  # $10.00
                "description": f"Invoice for {customer['name']}",
                "customer_email": customer["email"],
                "customer_name": customer["name"]
            }
            
            response = await client.post(
                "http://localhost:8000/payments/create",
                json=payment_data
            )
            
            payment = response.json()
            payments.append(payment)
            print(f"Created payment for {customer['name']}: {payment['payment_id']}")
        
        return payments


# Example 4: Payment status tracking
async def example_payment_tracking():
    """Track payment status"""
    async with httpx.AsyncClient() as client:
        # Create a payment first
        payment_data = {
            "amount": 7500,  # $75.00
            "description": "Order #ABC123",
            "customer_email": "tracking@example.com",
            "customer_name": "Tracking Customer"
        }
        
        response = await client.post(
            "http://localhost:8000/payments/create",
            json=payment_data
        )
        
        payment = response.json()
        payment_id = payment['payment_id']
        
        # Check status multiple times
        for i in range(3):
            status_response = await client.get(
                f"http://localhost:8000/payments/{payment_id}"
            )
            
            status = status_response.json()
            print(f"Check {i+1} - Status: {status['status']}")
            print(f"  Amount: ${status['amount']/100:.2f} {status['currency'].upper()}")
            print(f"  Customer: {status['metadata']['customer_name']}")
            
            if i < 2:
                await asyncio.sleep(2)  # Wait between checks


# Example 5: Refund workflow
async def example_refund_workflow():
    """Handle payment refunds"""
    async with httpx.AsyncClient() as client:
        # Create a payment
        payment_data = {
            "amount": 10000,  # $100.00
            "description": "Product purchase",
            "customer_email": "refund@example.com",
            "customer_name": "Refund Tester"
        }
        
        response = await client.post(
            "http://localhost:8000/payments/create",
            json=payment_data
        )
        
        payment = response.json()
        payment_id = payment['payment_id']
        
        print(f"Created payment: {payment_id}")
        print(f"Status: {payment['status']}")
        
        # Simulate payment confirmation
        print("Waiting for payment to be processed...")
        await asyncio.sleep(2)
        
        # Check status
        status_response = await client.get(
            f"http://localhost:8000/payments/{payment_id}"
        )
        status = status_response.json()
        print(f"Current status: {status['status']}")
        
        # If succeeded, refund it
        if status['status'] == 'succeeded':
            refund_data = {
                "payment_id": payment_id,
                "reason": "duplicate"
            }
            
            refund_response = await client.post(
                f"http://localhost:8000/payments/{payment_id}/refund",
                json=refund_data
            )
            
            refund = refund_response.json()
            print(f"Refund created: {refund['refund_id']}")
            print(f"Refund status: {refund['status']}")
            print(f"Refund amount: ${refund['amount']/100:.2f}")


# Example 6: Error handling
async def example_error_handling():
    """Handle API errors gracefully"""
    async with httpx.AsyncClient() as client:
        # Try invalid payment
        try:
            invalid_payment = {
                "amount": -1000,  # Negative amount
                "description": "Invalid",
                "customer_email": "test@example.com",
                "customer_name": "Test"
            }
            
            response = await client.post(
                "http://localhost:8000/payments/create",
                json=invalid_payment
            )
            
            if response.status_code != 200:
                error = response.json()
                print(f"Error: {error['detail']}")
            
        except Exception as e:
            print(f"Exception caught: {e}")


async def main():
    """Run examples"""
    print("=== Stripe Payment Integration Examples ===\n")
    
    print("1. Simple Payment Example")
    print("-" * 40)
    try:
        # await example_simple_payment()
        print("Skipped (requires API running)")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Saved Card Payment Example")
    print("-" * 40)
    print("Skipped (requires valid payment method ID from Stripe)")
    
    print("\n3. Bulk Payments Example")
    print("-" * 40)
    print("Use the test_payments.py script for bulk testing")
    
    print("\n4. Payment Tracking Example")
    print("-" * 40)
    print("Example code available - run with API server running")
    
    print("\n5. Refund Workflow Example")
    print("-" * 40)
    print("Example code available - requires payment in succeeded state")
    
    print("\n=== To run examples ===")
    print("1. Start the FastAPI server: uvicorn main:app --reload")
    print("2. Update the API endpoint in this file if needed")
    print("3. Uncomment example calls in main() function")


if __name__ == "__main__":
    asyncio.run(main())
