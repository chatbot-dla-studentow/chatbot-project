"""Agent 2 - Ticket Classification
Agent do klasyfikacji zgłoszeń - komunikuje się z Agent1 Student dla wiedzy
"""
import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

# Konfiguracja
AGENT1_URL = os.getenv("AGENT1_URL", "http://agent1_student:8001")

app = FastAPI(title="Agent 2 - Ticket Classification")

class TicketRequest(BaseModel):
    input: str
    user_id: Optional[str] = "anonymous"
    metadata: Optional[Dict] = {}

@app.post("/run")
async def process_ticket(payload: TicketRequest):
    """
    Klasyfikuje zgłoszenie.
    Może komunikować się z Agent1 dla wiedzy o procedurach.
    """
    try:
        # Możliwość zapytania Agent1 o wiedzę
        # Przykład: jeśli zgłoszenie dotyczy procedur studenckich
        ticket_text = payload.input.lower()
        
        # Podstawowa klasyfikacja
        classification = {
            "category": "inne",
            "priority": "medium",
            "agent": "agent2_ticket"
        }
        
        # Jeśli zgłoszenie związane z wiedzą studencka
        if any(word in ticket_text for word in ["stypendium", "egzamin", "urlop", "zawświadczenie"]):
            # Zapytaj Agent1 o procedury
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(
                        f"{AGENT1_URL}/api/chat",
                        json={
                            "messages": [
                                {"role": "user", "content": f"Jaka jest procedura dla: {payload.input}"}
                            ],
                            "model": "mistral:7b",
                            "stream": False
                        }
                    )
                    
                    if response.status_code == 200:
                        agent1_data = response.json()
                        classification["knowledge_from_agent1"] = agent1_data.get("message", {}).get("content", "")
                        classification["sources"] = agent1_data.get("sources", {})
                        classification["category"] = "akademickie"
                except Exception as e:
                    classification["agent1_error"] = str(e)
        
        return {
            "ticket_classification": classification,
            "input": payload.input
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agent": "agent2_ticket",
        "agent1_connection": AGENT1_URL
    }
