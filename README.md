# Stripe FastAPI Payment Integration

A FastAPI application for integrating Stripe payments in a vendor sandbox environment. This project demonstrates how to create, manage, and refund payments using Stripe's API.

## Features

- 🔐 Secure payment processing with Stripe
- 💳 Customer management
- 💰 Payment creation and confirmation
- ↩️ Payment refunds
- 📊 Payment status tracking
- 🧪 Comprehensive test suite
- 📚 Auto-generated API documentation

## Prerequisites

- Python 3.8+
- Stripe account (free sandbox account at https://stripe.com)
- Stripe API keys (test keys for development)

## Installation

1. **Clone or create the project:**
   ```bash
   cd /home/spgadmin/Documents/stripe
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Stripe credentials:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Stripe test keys:
     - Get keys from: https://dashboard.stripe.com/apikeys
     - Use the **restricted API keys** for better security
     ```
     STRIPE_SECRET_KEY=sk_test_your_key_here
     STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
     STRIPE_WEBHOOK_SECRET=whsec_test_secret_here
     ```

## Running the Application

### Start the FastAPI server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Access API Documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Payments

- `POST /payments/create` - Create a new payment intent
- `POST /payments/{payment_id}/confirm` - Confirm a payment
- `GET /payments/{payment_id}` - Get payment status
- `POST /payments/{payment_id}/refund` - Refund a payment

### Customers

- `POST /customers/create` - Create a new customer
- `GET /customers/{customer_id}/payment-methods` - List customer's payment methods

### Health

- `GET /` - Health check endpoint

## Testing

### Run the comprehensive test suite:

```bash
python test_payments.py
```

This will:
1. Check API health
2. Create sample customers
3. Create sample payments
4. Check payment status
5. List payment methods
6. Display test card numbers and next steps

### Test Card Numbers

Use these card numbers in Stripe's test mode:

| Type | Card Number | Status |
|------|-------------|--------|
| Success | 4242 4242 4242 4242 | Succeeds |
| Decline | 4000 0000 0000 0002 | Declined |
| Auth Required | 4000 0025 0000 3155 | Requires 3D Secure |

- **Expiry**: Any future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)

## Project Structure

```
stripe/
├── main.py              # FastAPI application and endpoints
├── config.py            # Configuration and environment setup
├── models.py            # Pydantic request/response models
├── stripe_service.py    # Stripe API service methods
├── test_payments.py     # Test suite with sample data
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .env                 # Local environment variables (create from .env.example)
└── README.md            # This file
```

## Example Usage

### Create a Payment

```bash
curl -X POST "http://localhost:8000/payments/create" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "description": "Order #12345",
    "customer_email": "customer@example.com",
    "customer_name": "John Doe"
  }'
```

### Check Payment Status

```bash
curl -X GET "http://localhost:8000/payments/pi_1234567890" \
  -H "Content-Type: application/json"
```

### Refund a Payment

```bash
curl -X POST "http://localhost:8000/payments/pi_1234567890/refund" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "requested_by_customer"
  }'
```

## Environment Variables

Create a `.env` file in the project root:

```env
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_test_secret_here
DEBUG=True
```

## Security Notes

1. **Never commit `.env` file** - Add it to `.gitignore`
2. **Use restricted keys** - Stripe recommends using restricted API keys
3. **Validate all inputs** - Always validate customer data
4. **Use HTTPS** - Always use HTTPS in production
5. **Secure your API** - Implement authentication and rate limiting
6. **Handle webhooks securely** - Verify webhook signatures

## Webhook Integration (Optional)

For production, you should handle Stripe webhooks to listen for payment events:

1. Set your webhook endpoint URL in Stripe Dashboard
2. Implement a webhook route to handle events like `payment_intent.succeeded`
3. Verify webhook signatures using `STRIPE_WEBHOOK_SECRET`

### Local webhook testing (Stripe CLI or ngrok)

Use the Stripe CLI to forward events from your Stripe account to your local `webhook` endpoint:

```bash
# Install the Stripe CLI (https://stripe.com/docs/stripe-cli)
stripe listen --forward-to http://localhost:8000/webhook
```

If you prefer `ngrok`, expose your local server and configure the webhook URL in the Stripe Dashboard:

```bash
# Start the server locally
# uvicorn main:app --reload --port 8000

# Start ngrok to forward to port 8000
ngrok http 8000

# In the Stripe Dashboard, set the webhook endpoint to the ngrok URL + /webhook
```

When using the Stripe CLI it will also print the `--forward-to` and sign the events for you. To verify signatures locally, copy the `Signing secret` from the Stripe CLI output or Dashboard into your `.env` as `STRIPE_WEBHOOK_SECRET`.

### Example: testing a `payment_intent.succeeded` event

1. Create a test payment using the API or Dashboard.
2. Use the Stripe CLI to trigger a test event:

```bash
stripe trigger payment_intent.succeeded
```

3. The forwarded event will hit `http://localhost:8000/webhook` and your app will verify the signature and return a JSON acknowledgement.

## Card tokenization example (SetupIntent)

This repo includes a minimal frontend example that demonstrates how to tokenize card details
using Stripe.js and a `SetupIntent` so you can save a card to a Stripe `Customer` without
handling raw card numbers on your server.

- Example HTML: `static/save_card.html`

Usage:

1. Start the FastAPI server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Create a customer using the API (`POST /customers/create`) and note the `customer_id`.
3. Open `static/save_card.html` in a browser (or serve it via a static server), update the
  `PUBLISHABLE_KEY` and `CUSTOMER_ID` placeholders in the file, then click **Save card**.

What happens:

- The page requests a SetupIntent client secret from `/customers/{customer_id}/setup-intent`.
- Stripe.js calls `confirmCardSetup(client_secret, { payment_method: { card }})` to tokenize the card.
- On success the saved `payment_method` id (pm_...) is available in the `setupIntent` object.
- Since the SetupIntent was created with the `customer`, Stripe attaches the PaymentMethod to that customer automatically.

Security note: Do not place your secret key in the frontend. Use the publishable key only.

## Troubleshooting

### "API Key error"
- Verify your keys are copied correctly from https://dashboard.stripe.com/apikeys
- Ensure `.env` file is in the project root
- Check that you're using **test** keys (starting with `sk_test_` or `pk_test_`)

### "Connection refused"
- Ensure the FastAPI server is running on port 8000
- Check for port conflicts: `lsof -i :8000`

### "Payment declined"
- Use `4242 4242 4242 4242` for successful test payments
- Check that test mode is enabled in Stripe Dashboard

## Resources

- [Stripe API Documentation](https://stripe.com/docs/api)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Stripe Checkout (Hosted Payment Page)

Instead of handling card details on your server, redirect users to Stripe's hosted checkout page.
This is simpler, more secure, and better for PCI compliance.

### Usage

1. Create a checkout session:

```bash
curl -X POST "http://localhost:8000/checkout/create?customer_id=cus_XXXXXXXX&amount=5000&description=Premium%20Subscription"
```

The response includes a `checkout_url` — redirect the user there.

2. User enters card details on Stripe's secure page.
3. On success, Stripe redirects to `/checkout/success?session_id=cs_...`
4. On cancel, Stripe redirects to `/checkout/cancel`

### HTML Example

Open [http://localhost:8000/static/checkout.html](http://localhost:8000/static/checkout.html) to test interactively.

Enter a customer ID, amount, and description, then click "Create Checkout Session & Redirect".
You'll be taken to Stripe's hosted checkout page.

### API Endpoints

- `POST /checkout/create` - Create a checkout session and get redirect URL
- `GET /checkout/session/{session_id}` - Get session status
- `GET /checkout/success` - Callback after successful payment
- `GET /checkout/cancel` - Callback if user cancels

## License

This project is provided as-is for educational purposes.
