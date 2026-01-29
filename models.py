from pydantic import BaseModel, Field
from typing import Optional


class PaymentRequest(BaseModel):
    """Request model for creating a payment"""
    amount: int = Field(..., gt=0, description="Amount in cents (e.g., 1000 for $10.00)")
    currency: str = Field(default="usd", description="Currency code")
    description: str = Field(..., description="Payment description")
    customer_email: str = Field(..., description="Customer email address")
    customer_name: str = Field(..., description="Customer name")
    payment_method_id: str = Field(default=None, description="Stripe PaymentMethod ID")
    
    
class PaymentResponse(BaseModel):
    """Response model for payment creation"""
    payment_id: str
    status: str
    amount: int
    currency: str
    customer_email: str
    client_secret: Optional[str] = None
    

class CustomerRequest(BaseModel):
    """Request model for creating a customer"""
    email: str = Field(..., description="Customer email")
    name: str = Field(..., description="Customer name")
    description: Optional[str] = Field(None, description="Customer description")


class CustomerResponse(BaseModel):
    """Response model for customer creation"""
    customer_id: str
    email: str
    name: str


class RefundRequest(BaseModel):
    """Request model for refunding a payment"""
    payment_id: str = Field(..., description="Stripe PaymentIntent ID")
    reason: Optional[str] = Field(None, description="Refund reason")


class RefundResponse(BaseModel):
    """Response model for refund"""
    refund_id: str
    status: str
    amount: int
    payment_id: str


class PaymentStatusResponse(BaseModel):
    """Response model for payment status"""
    payment_id: str
    status: str
    amount: int
    currency: str
    customer_email: str
    created_at: int


class PaymentMethodCardRequest(BaseModel):
    """Request model for creating a card payment method"""
    card_number: str = Field(..., description="Credit card number (16 digits)")
    exp_month: int = Field(..., ge=1, le=12, description="Expiration month (1-12)")
    exp_year: int = Field(..., ge=2024, description="Expiration year (4 digits)")
    cvc: str = Field(..., description="Card verification code (3-4 digits)")
    billing_name: Optional[str] = Field(None, description="Billing name for the card")
    billing_email: Optional[str] = Field(None, description="Billing email for the card")


class PaymentMethodResponse(BaseModel):
    """Response model for payment method"""
    payment_method_id: str
    type: str
    card: dict = Field(..., description="Card details (brand, last4, exp_month, exp_year)")
    billing_details: Optional[dict] = None


class PaymentMethodListResponse(BaseModel):
    """Response model for listing payment methods"""
    payment_method_id: str
    type: str
    card: dict
    billing_details: Optional[dict] = None
