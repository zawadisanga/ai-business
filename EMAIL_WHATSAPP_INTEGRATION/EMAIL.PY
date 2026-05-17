# email_whatsapp_integration/email.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sendgrid
from sendgrid.helpers.mail import Mail
import os

router = APIRouter()

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    from_email: str = "noreply@blooai.com"

class EmailResponse(BaseModel):
    success: bool
    message: str

# Initialize SendGrid
sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY", ""))

@router.post("/send", response_model=EmailResponse)
async def send_email(request: EmailRequest):
    """
    Send email using SendGrid
    """
    try:
        message = Mail(
            from_email=request.from_email,
            to_emails=request.to_email,
            subject=request.subject,
            html_content=f"<html><body>{request.body}</body></html>"
        )
        
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            return EmailResponse(
                success=True,
                message="Email sent successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/welcome")
async def send_welcome_email(email: str, name: str):
    """
    Send welcome email to new user
    """
    subject = "Welcome to Bloo AI! 🎉"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <h1 style="color: #667eea;">Welcome to Bloo AI, {name}!</h1>
        <p>Thank you for joining Bloo AI - the first complete AI Business Operating System for Africa.</p>
        
        <h2>Getting Started:</h2>
        <ol>
            <li>Complete your business profile</li>
            <li>Try our AI CEO for strategic advice</li>
            <li>Set up your first automation</li>
        </ol>
        
        <div style="background: #f8fafc; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <p><strong>Need help?</strong> Reply to this email or chat with our AI Support.</p>
            <p><strong>Dashboard:</strong> <a href="https://yourdomain.com/dashboard">Click here</a></p>
        </div>
        
        <p>Best regards,<br>Bloo AI Team</p>
        <hr>
        <p style="font-size: 12px; color: #94a3b8;">© 2024 Bloo AI - Built for African Businesses</p>
    </div>
    """
    
    return await send_email(EmailRequest(
        to_email=email,
        subject=subject,
        body=body
    ))
