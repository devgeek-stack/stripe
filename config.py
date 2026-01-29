import os
from dotenv import load_dotenv

load_dotenv()

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test")

# API Configuration
API_TITLE = "Stripe Payment Integration"
API_VERSION = "1.0.0"

# Payment Configuration
CURRENCY = "usd"
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_")
