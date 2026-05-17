# agents/ceo_agent.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

router = APIRouter()

class CEOAdviceRequest(BaseModel):
    revenue: float = 50000
    costs: float = 35000
    customers: int = 150
    industry: str = "general"

class CEOAdviceResponse(BaseModel):
    success: bool
    data: dict
    timestamp: str

@router.post("/advice", response_model=CEOAdviceResponse)
async def get_ceo_advice(request: CEOAdviceRequest):
    """
    AI CEO - Provides strategic business advice
    """
    profit = request.revenue - request.costs
    profit_margin = (profit / request.revenue * 100) if request.revenue > 0 else 0
    avg_customer_value = (request.revenue / request.customers) if request.customers > 0 else 0
    
    # Determine business health
    if profit_margin < 10:
        health = "critical"
        advice = [
            f"⚠️ CRITICAL: Your profit margin is only {profit_margin:.1f}%",
            "Your business is at risk. Immediate action required."
        ]
        actions = [
            "Reduce operational costs by 20-30% immediately",
            "Increase prices by 10-15% for all customers",
            "Cut all non-essential marketing spend"
        ]
    elif profit_margin < 25:
        health = "warning"
        advice = [
            f"📊 WARNING: Profit margin at {profit_margin:.1f}%",
            "Room for improvement in operations and pricing"
        ]
        actions = [
            "Optimize supply chain to save 5-8% on costs",
            "Implement customer loyalty program",
            "Automate repetitive tasks"
        ]
    else:
        health = "excellent"
        advice = [
            f"✅ EXCELLENT: Profit margin of {profit_margin:.1f}%",
            "Your business is performing well. Time to scale aggressively."
        ]
        actions = [
            "Invest 30% of profits into marketing",
            "Expand to 2 new markets or regions",
            "Hire additional sales staff"
        ]
    
    # Generate forecast
    forecast = []
    projected_revenue = request.revenue
    for i in range(1, 7):
        growth_rate = 0.15 if profit_margin > 25 else (0.08 if profit_margin > 10 else 0.03)
        projected_revenue = projected_revenue * (1 + growth_rate)
        forecast.append({
            "month": i,
            "revenue": round(projected_revenue),
            "profit": round(projected_revenue * (profit_margin / 100))
        })
    
    return CEOAdviceResponse(
        success=True,
        data={
            "analysis": {
                "revenue": f"${request.revenue:,.0f}",
                "costs": f"${request.costs:,.0f}",
                "profit": f"${profit:,.0f}",
                "profit_margin": f"{profit_margin:.1f}%",
                "avg_customer_value": f"${avg_customer_value:.2f}",
                "health": health
            },
            "advice": advice,
            "actions": actions,
            "forecast": forecast,
            "timestamp": datetime.now().isoformat()
        },
        timestamp=datetime.now().isoformat()
    )

@router.get("/market-analysis/{industry}")
async def get_market_analysis(industry: str):
    """Get market analysis for specific industry"""
    market_data = {
        "technology": {
            "size": "$5.2T",
            "growth": "8.5%",
            "trends": ["AI Integration", "Cloud Migration", "Cybersecurity"],
            "opportunities": ["SME Automation", "Vertical SaaS"]
        },
        "ecommerce": {
            "size": "$6.3T",
            "growth": "12%",
            "trends": ["Mobile Shopping", "Social Commerce"],
            "opportunities": ["DTC Brands", "Subscription Boxes"]
        }
    }
    return market_data.get(industry, {"message": "Industry data not available"})
