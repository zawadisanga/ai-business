# agents/support_agent.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    language: str = "en"

class ChatResponse(BaseModel):
    success: bool
    response: str
    intent: str
    language: str
    timestamp: str

# Multi-language responses
RESPONSES = {
    "en": {
        "greeting": "Welcome! How can I help you today?",
        "payment": "Your payment is being processed securely. Takes 1-3 business days.",
        "refund": "Refund requests are processed within 5-7 business days.",
        "shipping": "Standard shipping takes 3-5 business days.",
        "hours": "Our support team is available 24/7, 365 days a year.",
        "technical": "Please describe the technical issue you are experiencing.",
        "complaint": "I apologize for the inconvenience. Let me help resolve this issue.",
        "default": "Thank you for contacting Bloo AI support. How else can I assist you today?"
    },
    "sw": {
        "greeting": "Karibu! Ninaweza kukusaidia vipi leo?",
        "payment": "Malipo yako yanachakatwa kwa usalama. Inachukua siku 1-3 za kazi.",
        "refund": "Ombi la refund linachukua siku 5-7 za kazi.",
        "shipping": "Usafirishaji wa kawaida unachukua siku 3-5.",
        "hours": "Timu yetu inapatikana saa 24/7, siku zote za mwaka.",
        "default": "Asante kwa kuwasiliana nasi. Tunasubiri kukusaidia zaidi."
    },
    "fr": {
        "greeting": "Bienvenue! Comment puis-je vous aider aujourd'hui?",
        "payment": "Votre paiement est traité de manière sécurisée.",
        "default": "Merci de nous contacter. Comment puis-je vous aider davantage?"
    }
}

@router.post("/chat", response_model=ChatResponse)
async def support_chat(request: ChatRequest):
    """
    AI Support Agent - 24/7 multilingual customer support
    """
    msg = request.message.lower()
    lang = request.language if request.language in RESPONSES else "en"
    
    responses = RESPONSES[lang]
    intent = "general"
    response = responses.get("default", RESPONSES["en"]["default"])
    
    # Intent detection
    if any(word in msg for word in ["hello", "hi", "karibu", "bonjour"]):
        response = responses.get("greeting", RESPONSES["en"]["greeting"])
        intent = "greeting"
    elif any(word in msg for word in ["payment", "pay", "malipo", "paiement"]):
        response = responses.get("payment", RESPONSES["en"]["payment"])
        intent = "payment"
    elif any(word in msg for word in ["refund", "return", "rejesha"]):
        response = responses.get("refund", RESPONSES["en"]["refund"])
        intent = "refund"
    elif any(word in msg for word in ["shipping", "delivery", "usafirishaji"]):
        response = responses.get("shipping", RESPONSES["en"]["shipping"])
        intent = "shipping"
    elif any(word in msg for word in ["hour", "time", "saa", "open"]):
        response = responses.get("hours", RESPONSES["en"]["hours"])
        intent = "hours"
    elif any(word in msg for word in ["technical", "error", "bug", "not working"]):
        response = responses.get("technical", RESPONSES["en"]["technical"])
        intent = "technical"
    elif any(word in msg for word in ["complaint", "angry", "bad", "terrible"]):
        response = responses.get("complaint", RESPONSES["en"]["complaint"])
        intent = "complaint"
    
    return ChatResponse(
        success=True,
        response=response,
        intent=intent,
        language=lang,
        timestamp=datetime.now().isoformat()
    )
