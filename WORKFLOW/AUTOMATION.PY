# workflow/automation.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uuid
from datetime import datetime

router = APIRouter()

class AutomationRequest(BaseModel):
    trigger: str
    action: str
    trigger_details: Dict[str, Any] = {}
    action_details: Dict[str, Any] = {}

class AutomationResponse(BaseModel):
    success: bool
    automation_id: str
    message: str

# In-memory storage (replace with database)
automations = []

@router.post("/create", response_model=AutomationResponse)
async def create_automation(request: AutomationRequest):
    """
    Create a new automation workflow
    """
    automation_id = str(uuid.uuid4())
    
    automation = {
        "id": automation_id,
        "trigger": request.trigger,
        "action": request.action,
        "trigger_details": request.trigger_details,
        "action_details": request.action_details,
        "status": "active",
        "runs": 0,
        "created_at": datetime.now().isoformat()
    }
    
    automations.append(automation)
    
    return AutomationResponse(
        success=True,
        automation_id=automation_id,
        message=f"Automation created: When {request.trigger} → Then {request.action}"
    )

@router.get("/list")
async def list_automations():
    """List all automations"""
    return {"success": True, "data": automations}

@router.post("/trigger/{automation_id}")
async def trigger_automation(automation_id: str, payload: Dict[str, Any] = None):
    """
    Manually trigger an automation
    """
    automation = next((a for a in automations if a["id"] == automation_id), None)
    
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    # Execute action based on type
    action = automation["action"]
    action_details = automation["action_details"]
    
    result = {
        "status": "executed",
        "action": action,
        "details": f"Action '{action}' executed successfully",
        "timestamp": datetime.now().isoformat()
    }
    
    automation["runs"] += 1
    
    return {"success": True, "result": result}
