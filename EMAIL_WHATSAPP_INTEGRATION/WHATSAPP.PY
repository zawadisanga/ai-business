# email_whatsapp_integration/whatsapp.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from twilio.rest import Client
import os

router = APIRouter()

class WhatsAppRequest(BaseModel):
    to_number: str
    message: str

class WhatsAppResponse(BaseModel):
    success: bool
    message: str

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

@router.post("/send", response_model=WhatsAppResponse)
async def send_whatsapp(request: WhatsAppRequest):
    """
    Send WhatsApp message using Twilio
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=request.message,
            to=f"whatsapp:{request.to_number}"
        )
        
        return WhatsAppResponse(
            success=True,
            message=f"Message sent with SID: {message.sid}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/order-confirmation")
async def send_order_confirmation(phone: str, product_name: str, amount: float):
    """
    Send order confirmation via WhatsApp
    """
    message = f"""
    ✅ *Order Confirmation - Bloo AI*
    
    Product: {product_name}
    Amount: ${amount}
    
    You will receive download instructions shortly.
    
    Need help? Reply to this message.
    Thank you for your purchase!
    """
    
    return await send_whatsapp(WhatsAppRequest(
        to_number=phone,
        message=message
    ))
