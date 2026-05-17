# payment_system/mpesa.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import uuid
import os
from datetime import datetime
import requests
import base64

router = APIRouter()

class MpesaPaymentRequest(BaseModel):
    amount: float
    phone_number: str
    reference: str = None

class MpesaPaymentResponse(BaseModel):
    success: bool
    message: str
    transaction_id: str
    checkout_request_id: str = None

# M-Pesa API credentials (set in .env)
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")  # sandbox or production

def get_mpesa_token():
    """Get M-Pesa OAuth token"""
    if MPESA_ENVIRONMENT == "production":
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    else:
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    auth = base64.b64encode(f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise HTTPException(status_code=500, detail="Failed to get M-Pesa token")

@router.post("/stkpush", response_model=MpesaPaymentResponse)
async def mpesa_stkpush(request: MpesaPaymentRequest):
    """
    Initiate M-Pesa STK Push (customer receives payment prompt on phone)
    """
    if not request.phone_number or not request.amount:
        raise HTTPException(status_code=400, detail="Phone number and amount required")
    
    # Clean phone number
    phone = request.phone_number.replace("+", "").replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif not phone.startswith("254"):
        phone = "254" + phone
    
    transaction_id = request.reference or str(uuid.uuid4())
    
    if MPESA_ENVIRONMENT == "sandbox":
        # Simulate payment for testing
        return MpesaPaymentResponse(
            success=True,
            message=f"Test payment of {request.amount} KES from {phone}",
            transaction_id=transaction_id,
            checkout_request_id="ws_CO_191220240001234567"
        )
    
    # Production - actual M-Pesa API call
    try:
        token = get_mpesa_token()
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()
        ).decode()
        
        url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(request.amount),
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": "https://yourdomain.com/api/payments/mpesa/callback",
            "AccountReference": transaction_id,
            "TransactionDesc": f"Bloo AI Payment - {transaction_id[:8]}"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return MpesaPaymentResponse(
                success=True,
                message="STK Push sent successfully. Please check your phone.",
                transaction_id=transaction_id,
                checkout_request_id=data.get("CheckoutRequestID")
            )
        else:
            raise HTTPException(status_code=500, detail="M-Pesa request failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/callback")
async def mpesa_callback(request: Request):
    """
    M-Pesa callback endpoint (receives payment confirmation)
    """
    callback_data = await request.json()
    
    # Log the callback
    print("M-Pesa Callback Received:", callback_data)
    
    # Process payment confirmation
    # Update transaction status in database
    # Send email/whatsapp confirmation to customer
    # Give user access to purchased product
    
    return {"ResultCode": 0, "ResultDesc": "Success"}
