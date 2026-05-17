# main.py - Bloo AI Main Entry Point
import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import modules
from backend.database import init_db, get_db
from auth import router as auth_router
from admin import router as admin_router
from billing import router as billing_router
from enterprise import router as enterprise_router
from agents.ceo_agent import router as ceo_router
from agents.sales_agent import router as sales_router
from agents.support_agent import router as support_router
from agents.hr_agent import router as hr_router
from agents.accountant_agent import router as accountant_router
from workflow.automation import router as automation_router
from payment_system.mpesa import router as mpesa_router
from payment_system.stripe import router as stripe_router
from email_whatsapp_integration.email import router as email_router
from email_whatsapp_integration.whatsapp import router as whatsapp_router

load_dotenv()

app = FastAPI(
    title="Bloo AI - Business Operating System",
    description="Complete AI Business OS for Africa",
    version="5.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(billing_router, prefix="/api/billing", tags=["Billing"])
app.include_router(enterprise_router, prefix="/api/enterprise", tags=["Enterprise"])
app.include_router(ceo_router, prefix="/api/ceo", tags=["AI CEO"])
app.include_router(sales_router, prefix="/api/sales", tags=["AI Sales"])
app.include_router(support_router, prefix="/api/support", tags=["AI Support"])
app.include_router(hr_router, prefix="/api/hr", tags=["AI HR"])
app.include_router(accountant_router, prefix="/api/accountant", tags=["AI Accountant"])
app.include_router(automation_router, prefix="/api/automation", tags=["Automation"])
app.include_router(mpesa_router, prefix="/api/payments/mpesa", tags=["M-Pesa"])
app.include_router(stripe_router, prefix="/api/payments/stripe", tags=["Stripe"])
app.include_router(email_router, prefix="/api/communication/email", tags=["Email"])
app.include_router(whatsapp_router, prefix="/api/communication/whatsapp", tags=["WhatsApp"])

@app.on_event("startup")
async def startup_event():
    await init_db()
    print("✅ Bloo AI System Started Successfully!")
    print("🚀 API running on http://localhost:8000")
    print("🤖 AI Agents: CEO | Sales | Support | HR | Accountant")
    print("💳 Payment Systems: M-Pesa | Stripe | PayPal")

@app.get("/")
async def root():
    return {
        "name": "Bloo AI - Business Operating System",
        "version": "5.0.0",
        "status": "operational",
        "agents": ["CEO", "Sales", "Support", "HR", "Accountant"],
        "payment_systems": ["M-Pesa", "Stripe", "PayPal"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
