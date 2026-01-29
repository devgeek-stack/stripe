import stripe
from config import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, CURRENCY
from models import PaymentResponse, CustomerResponse, RefundResponse
from typing import Optional

stripe.api_key = STRIPE_SECRET_KEY


class StripeService:
    """Service class for Stripe operations"""
    
    @staticmethod
    def create_payment(
        amount: int,
        description: str,
        customer_email: str,
        customer_name: str,
        payment_method_id: Optional[str] = None
    ) -> PaymentResponse:
        """
        Create a payment intent in Stripe
        
        Args:
            amount: Amount in cents
            description: Payment description
            customer_email: Customer email
            customer_name: Customer name
            payment_method_id: Optional PaymentMethod ID for saved cards
            
        Returns:
            PaymentResponse with payment details
        """
        try:
            # Create or retrieve customer
            customer = stripe.Customer.create(
                email=customer_email,
                name=customer_name,
                description=f"Payment from {customer_name}"
            )
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=CURRENCY,
                customer=customer.id,
                description=description,
                payment_method=payment_method_id,
                confirm=False if not payment_method_id else True,
                metadata={
                    "customer_name": customer_name,
                    "customer_email": customer_email
                }
            )
            
            return PaymentResponse(
                payment_id=payment_intent.id,
                status=payment_intent.status,
                amount=payment_intent.amount,
                currency=payment_intent.currency,
                customer_email=customer_email,
                client_secret=payment_intent.client_secret
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def confirm_payment(payment_id: str) -> PaymentResponse:
        """
        Confirm a payment intent
        
        Args:
            payment_id: PaymentIntent ID
            
        Returns:
            PaymentResponse with updated payment details
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
            
            return PaymentResponse(
                payment_id=payment_intent.id,
                status=payment_intent.status,
                amount=payment_intent.amount,
                currency=payment_intent.currency,
                customer_email=payment_intent.customer_email,
                client_secret=payment_intent.client_secret
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def get_payment_status(payment_id: str) -> dict:
        """
        Get the status of a payment
        
        Args:
            payment_id: PaymentIntent ID
            
        Returns:
            Payment details dictionary
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
            
            return {
                "payment_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "customer": payment_intent.customer,
                "created_at": payment_intent.created,
                "metadata": payment_intent.metadata
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_customer(email: str, name: str, description: Optional[str] = None) -> CustomerResponse:
        """
        Create a customer in Stripe
        
        Args:
            email: Customer email
            name: Customer name
            description: Optional customer description
            
        Returns:
            CustomerResponse with customer details
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                description=description or f"Customer: {name}"
            )
            
            return CustomerResponse(
                customer_id=customer.id,
                email=customer.email,
                name=customer.name
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def refund_payment(payment_id: str, reason: Optional[str] = None) -> RefundResponse:
        """
        Refund a payment
        
        Args:
            payment_id: PaymentIntent ID
            reason: Optional refund reason
            
        Returns:
            RefundResponse with refund details
        """
        try:
            # First, retrieve the PaymentIntent to get the Charge ID
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
            
            if not payment_intent.charges.data:
                raise Exception("No charge found for this payment intent")
            
            charge_id = payment_intent.charges.data[0].id
            
            # Create a refund for the charge
            refund = stripe.Refund.create(
                charge=charge_id,
                reason=reason or "requested_by_customer",
                metadata={"original_payment_id": payment_id}
            )
            
            return RefundResponse(
                refund_id=refund.id,
                status=refund.status,
                amount=refund.amount,
                payment_id=payment_id
            )
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_payment_method(
        customer_id: str,
        card_number: str,
        exp_month: int,
        exp_year: int,
        cvc: str,
        billing_name: Optional[str] = None,
        billing_email: Optional[str] = None
    ) -> dict:
        """
        Create a card payment method and attach it to a customer
        
        Args:
            customer_id: Stripe Customer ID
            card_number: Credit card number
            exp_month: Card expiration month
            exp_year: Card expiration year
            cvc: Card security code
            billing_name: Optional billing name
            billing_email: Optional billing email
            
        Returns:
            PaymentMethod details dictionary
        """
        try:
            # Create a payment method with card details
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": card_number,
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                    "cvc": cvc
                },
                billing_details={
                    "name": billing_name,
                    "email": billing_email
                }
            )
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method.id,
                customer=customer_id
            )
            
            return {
                "payment_method_id": payment_method.id,
                "type": payment_method.type,
                "card": {
                    "brand": payment_method.card.brand,
                    "last4": payment_method.card.last4,
                    "exp_month": payment_method.card.exp_month,
                    "exp_year": payment_method.card.exp_year
                },
                "billing_details": payment_method.billing_details
            }
        except stripe.error.CardError as e:
            raise Exception(f"Card error: {e.user_message}")
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def list_payment_methods(customer_id: str) -> list:
        """
        List all payment methods for a customer
        
        Args:
            customer_id: Stripe Customer ID
            
        Returns:
            List of payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return [
                {
                    "id": pm.id,
                    "type": pm.type,
                    "card": {
                        "brand": pm.card.brand,
                        "last4": pm.card.last4,
                        "exp_month": pm.card.exp_month,
                        "exp_year": pm.card.exp_year
                    }
                }
                for pm in payment_methods.data
            ]
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
