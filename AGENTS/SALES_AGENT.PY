# agents/sales_agent.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
import random

router = APIRouter()

class OutreachRequest(BaseModel):
    prospect_name: str = "Prospect"
    prospect_industry: str = "Technology"
    prospect_size: str = "Small Business"
    product: Optional[str] = "Bloo AI"

class OutreachResponse(BaseModel):
    success: bool
    subject: str
    message: str
    follow_up: str
    suggested_response: str

@router.post("/outreach", response_model=OutreachResponse)
async def generate_outreach(request: OutreachRequest):
    """
    AI Sales Agent - Generates personalized outreach messages
    """
    templates = [
        {
            "subject": f"Boost {request.prospect_industry} revenue with AI automation",
            "body": f"""Hello {request.prospect_name},

I noticed your {request.prospect_size} {request.prospect_industry} business could benefit from AI automation. 

Our clients using Bloo AI see:
• 40% revenue increase within 90 days
• 30+ hours saved per week
• 70% reduction in manual tasks

Would you be open to a 10-minute demo this week?

Best regards,
Bloo AI Sales Team"""
        },
        {
            "subject": f"Save 20+ hours/week with Bloo AI",
            "body": f"""Hi {request.prospect_name},

Businesses in {request.prospect_industry} waste {request.prospect_size == 'Small Business' and '15' or '30+'} hours on repetitive tasks. 

Our AI agents automate 70% of manual work including:
• Customer support (24/7)
• Sales outreach
• HR screening
• Financial analysis

See how → [demo link]

Cheers,
Bloo AI"""
        },
        {
            "subject": f"Special offer for {request.prospect_industry} leaders",
            "body": f"""Dear {request.prospect_name},

For a limited time, we're offering {request.prospect_size} businesses in {request.prospect_industry} a 30% discount on our AI platform.

What you get:
• 5 specialized AI agents (CEO, HR, Support, Sales, Accountant)
• Complete business automation
• You own your data (self-hosted option)

Schedule a quick chat to learn more.

Best,
Bloo AI Team"""
        }
    ]
    
    selected = random.choice(templates)
    
    return OutreachResponse(
        success=True,
        subject=selected["subject"],
        message=selected["body"],
        follow_up=f"Follow up in 3 days with case study for {request.prospect_industry}",
        suggested_response="Yes, I'm interested. Please send more information!"
    )

@router.post("/lead-score")
async def score_lead(budget: float = None, timeline: str = None, authority: str = None, need: str = None):
    """Score a lead based on BANT criteria"""
    score = 0
    
    if budget and budget > 10000:
        score += 30
    elif budget and budget > 5000:
        score += 20
    elif budget and budget > 1000:
        score += 10
    
    if timeline == "immediate":
        score += 30
    elif timeline == "1-3 months":
        score += 20
    elif timeline == "3-6 months":
        score += 10
    
    if authority == "decision-maker":
        score += 20
    elif authority == "influencer":
        score += 10
    
    if need == "high":
        score += 20
    elif need == "medium":
        score += 10
    
    qualification = "cold"
    if score >= 80:
        qualification = "hot - contact immediately"
    elif score >= 60:
        qualification = "warm - nurture"
    elif score >= 40:
        qualification = "warm - research more"
    else:
        qualification = "cold - not ready"
    
    return {
        "success": True,
        "score": score,
        "qualification": qualification,
        "recommendation": "Priority follow-up today" if score >= 70 else "Add to nurture campaign"
    }
