"""Agent 5 - Security and Compliance
Agent bezpieczeństwa - komunikuje się z Agent1 Student dla polityk RODO
"""
import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

# Konfiguracja
AGENT1_URL = os.getenv("AGENT1_URL", "http://agent1_student:8001")

app = FastAPI(title="Agent 5 - Security")

class SecurityRequest(BaseModel):
    input: str
    user_id: Optional[str] = "anonymous"
    metadata: Optional[Dict] = {}

@app.post("/run")
async def process_security_check(payload: SecurityRequest):
    """
    Sprawdza zgodność z RODO i polityką bezpieczeństwa.
    Komunikuje się z Agent1 dla wiedzy o RODO i danych osobowych.
    """
    try:
        query_text = payload.input.lower()
        
        # Podstawowa walidacja
        audit = {
            "status": "checked",
            "agent": "agent5_security"
        }
        
        # Jeśli dotyczy danych osobowych lub RODO
        if any(word in query_text for word in ["rodo", "dane", "osobow", "prywatność", "ochrona"]):
            # Zapytaj Agent1 o polityki RODO
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(
                        f"{AGENT1_URL}/api/chat",
                        json={
                            "messages": [
                                {"role": "user", "content": f"Polityka RODO dla: {payload.input}"}
                            ],
                            "model": "mistral:7b",
                            "stream": False
                        }
                    )
                    
                    if response.status_code == 200:
                        agent1_data = response.json()
                        audit["policy_from_agent1"] = agent1_data.get("message", {}).get("content", "")
                        audit["sources"] = agent1_data.get("sources", {})
                        audit["compliance"] = "verified"
                except Exception as e:
                    audit["agent1_error"] = str(e)
                    audit["compliance"] = "error"
        
        return {
            "audit": audit,
            "input": payload.input
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agent": "agent5_security",
        "agent1_connection": AGENT1_URL
    }
