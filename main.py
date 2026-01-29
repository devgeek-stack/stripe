from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import stripe
import os

from config import API_TITLE, API_VERSION, STRIPE_SECRET_KEY, WEBHOOK_SECRET
from models import (
    PaymentRequest, PaymentResponse, CustomerRequest, CustomerResponse,
    RefundRequest, RefundResponse, PaymentStatusResponse,
    PaymentMethodCardRequest, PaymentMethodResponse
)
from stripe_service import StripeService

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Stripe Payment Integration API for Vendor Payments"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Stripe Payment Integration API",
        "version": API_VERSION
    }



@app.post("/webhook", tags=["Webhooks"])
async def stripe_webhook(request: Request):
    """Endpoint to receive Stripe webhook events.

    Verifies the Stripe signature using `WEBHOOK_SECRET` and handles
    common events like `payment_intent.succeeded` and
    `payment_intent.payment_failed`.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if sig_header is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing stripe-signature header")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError:
        # Invalid payload
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Handle the event types you care about
    event_type = event.get("type")

    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        # TODO: implement vendor fulfillment, notifications, bookkeeping, etc.
        return {"received": True, "type": event_type, "id": payment_intent.get("id")}

    if event_type == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        # TODO: implement failure handling (notify customer, retry logic, etc.)
        return {"received": True, "type": event_type, "id": payment_intent.get("id")}

    # Return a generic acknowledgement for unhandled events
    return {"received": True, "type": event_type}


@app.post("/payments/create", response_model=PaymentResponse, tags=["Payments"])
async def create_payment(payment: PaymentRequest) -> PaymentResponse:
    """
    Create a new payment intent
    
    - **amount**: Payment amount in cents (e.g., 1000 = $10.00)
    - **currency**: Currency code (default: usd)
    - **description**: Payment description
    - **customer_email**: Customer email address
    - **customer_name**: Customer name
    """
    try:
        response = StripeService.create_payment(
            amount=payment.amount,
            description=payment.description,
            customer_email=payment.customer_email,
            customer_name=payment.customer_name,
            payment_method_id=payment.payment_method_id
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/payments/{payment_id}/confirm", response_model=PaymentResponse, tags=["Payments"])
async def confirm_payment(payment_id: str) -> PaymentResponse:
    """
    Confirm a payment intent (after client-side confirmation)
    
    - **payment_id**: PaymentIntent ID from Stripe
    """
    try:
        response = StripeService.confirm_payment(payment_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/payments/{payment_id}", response_model=dict, tags=["Payments"])
async def get_payment_status(payment_id: str) -> dict:
    """
    Get the status of a payment
    
    - **payment_id**: PaymentIntent ID from Stripe
    """
    try:
        response = StripeService.get_payment_status(payment_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.post("/customers/create", response_model=CustomerResponse, tags=["Customers"])
async def create_customer(customer: CustomerRequest) -> CustomerResponse:
    """
    Create a new customer in Stripe
    
    - **email**: Customer email address
    - **name**: Customer name
    - **description**: Optional customer description
    """
    try:
        response = StripeService.create_customer(
            email=customer.email,
            name=customer.name,
            description=customer.description
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/customers/{customer_id}/payment-methods", response_model=PaymentMethodResponse, tags=["Customers"])
async def add_payment_method(customer_id: str, payment_method: PaymentMethodCardRequest) -> PaymentMethodResponse:
    """
    Add a credit card as a payment method to a customer
    
    - **customer_id**: Stripe Customer ID
    - **card_number**: 16-digit credit card number
    - **exp_month**: Card expiration month (1-12)
    - **exp_year**: Card expiration year (4 digits)
    - **cvc**: Card security code (3-4 digits)
    - **billing_name**: Optional billing name
    - **billing_email**: Optional billing email
    
    Note: In production, use client-side tokenization (Stripe.js/Elements) 
    to avoid handling card data on your server.
    """
    try:
        response = StripeService.create_payment_method(
            customer_id=customer_id,
            card_number=payment_method.card_number,
            exp_month=payment_method.exp_month,
            exp_year=payment_method.exp_year,
            cvc=payment_method.cvc,
            billing_name=payment_method.billing_name,
            billing_email=payment_method.billing_email
        )
        return PaymentMethodResponse(
            payment_method_id=response["payment_method_id"],
            type=response["type"],
            card=response["card"],
            billing_details=response["billing_details"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/customers/{customer_id}/setup-intent", tags=["Customers"])
async def create_setup_intent(customer_id: str):
    """Create a SetupIntent for a customer and return the client_secret.

    Use this on the server to request a client secret which the frontend
    will use with Stripe.js to tokenize card details (no raw card data
    goes through your server).
    """
    try:
        setup_intent = stripe.SetupIntent.create(
            customer=customer_id,
            payment_method_types=["card"],
            usage="off_session"
        )
        return {"client_secret": setup_intent.client_secret, "setup_intent_id": setup_intent.id}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/payments/{payment_id}/refund", response_model=RefundResponse, tags=["Refunds"])
async def refund_payment(payment_id: str, refund_request: RefundRequest) -> RefundResponse:
    """
    Refund a payment
    
    - **payment_id**: PaymentIntent ID from Stripe
    - **reason**: Optional refund reason (requested_by_customer, duplicate, fraudulent, etc.)
    """
    try:
        response = StripeService.refund_payment(
            payment_id=refund_request.payment_id,
            reason=refund_request.reason
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/customers/{customer_id}/payment-methods", tags=["Customers"])
async def list_payment_methods(customer_id: str) -> list:
    """
    List all payment methods for a customer
    
    - **customer_id**: Stripe Customer ID
    """
    try:
        response = StripeService.list_payment_methods(customer_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/checkout/create", tags=["Checkout"])
async def create_checkout_session(
    customer_id: str,
    amount: int,
    description: str,
    success_url: str = "http://localhost:8000/checkout/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url: str = "http://localhost:8000/checkout/cancel"
) -> dict:
    """
    Create a Stripe Checkout Session for payment
    
    User will be redirected to Stripe's hosted checkout page to enter card details.
    After payment, they are redirected back to your `success_url`.
    
    - **customer_id**: Stripe Customer ID
    - **amount**: Amount in cents (e.g., 5000 for $50.00)
    - **description**: Product/service description
    - **success_url**: URL to redirect on successful payment (use {CHECKOUT_SESSION_ID} placeholder)
    - **cancel_url**: URL to redirect if user cancels
    """
    try:
        response = StripeService.create_checkout_session(
            customer_id=customer_id,
            amount=amount,
            description=description,
            success_url=success_url,
            cancel_url=cancel_url
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/checkout/session/{session_id}", tags=["Checkout"])
async def get_checkout_session(session_id: str) -> dict:
    """
    Get checkout session details and payment status
    
    - **session_id**: Stripe Checkout Session ID
    """
    try:
        response = StripeService.get_checkout_session(session_id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/checkout/success", tags=["Checkout"])
async def checkout_success(session_id: str):
    """Callback page after successful payment (customize as needed)"""
    try:
        session_info = StripeService.get_checkout_session(session_id)
        return {
            "status": "success",
            "message": "Payment completed successfully!",
            "session": session_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/checkout/cancel", tags=["Checkout"])
async def checkout_cancel():
    """Callback page if user cancels payment"""
    return {"status": "cancelled", "message": "Payment was cancelled"}


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )
