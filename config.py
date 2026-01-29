import os
from dotenv import load_dotenv

load_dotenv()

# Stripe Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_51SupuWQLI8L4nEjIGiksKCv7GqVf9ZsZVNXJplpv9ezmk3yYQQ8VYajtHlm4KHYuxKoqK4feeHWvnqZpirAYY59M00SHM9OeX6")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_51SupuWQLI8L4nEjIpLGHKX6ZhKXmAJo6NmD9xvLbOyWZ00iQFCff0T5VMMRUTBpmMYBcARIVjZ4wvEBPqNYvpGV400Bj0RqxmK")

# API Configuration
API_TITLE = "Stripe Payment Integration"
API_VERSION = "1.0.0"

# Payment Configuration
CURRENCY = "usd"
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_test_secret_here")
