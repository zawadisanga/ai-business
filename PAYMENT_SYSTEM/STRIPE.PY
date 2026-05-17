# payment_system/stripe.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import stripe
import os

router = APIRouter()

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

class CheckoutRequest(BaseModel):
    product_name: str
    price: float
    quantity: int = 1

class CheckoutResponse(BaseModel):
    success: bool
    session_id: str
    url: str

@router.post("/create-checkout-session", response_model=CheckoutResponse)
async def create_checkout_session(request: CheckoutRequest):
    """
    Create Stripe Checkout Session
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": request.product_name,
                    },
                    "unit_amount": int(request.price * 100),  # Convert to cents
                },
                "quantity": request.quantity,
            }],
            mode="payment",
            success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://yourdomain.com/cancel",
        )
        
        return CheckoutResponse(
            success=True,
            session_id=session.id,
            url=session.url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Stripe webhook endpoint for payment confirmation
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Fulfill the purchase...
        print(f"Payment successful for session: {session['id']}")
    
    return {"status": "success"}
