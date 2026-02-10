"""Agent 3 - Analytics
Agent analityczny - komunikuje się z Agent1 Student dla danych
"""
import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

# Konfiguracja
AGENT1_URL = os.getenv("AGENT1_URL", "http://agent1_student:8001")

app = FastAPI(title="Agent 3 - Analytics")

class AnalyticsRequest(BaseModel):
    input: str
    user_id: Optional[str] = "anonymous"
    metadata: Optional[Dict] = {}

@app.post("/run")
async def analyze_data(payload: AnalyticsRequest):
    """
    Analizuje dane.
    Może komunikować się z Agent1 dla wiedzy o statystykach studenckich.
    """
    try:
        # Możliwość zapytania Agent1 o dane
        query_text = payload.input.lower()
        
        # Podstawowe insighty
        insights = {
            "summary": f"Analiza dla: {payload.input[:100]}",
            "agent": "agent3_analytics"
        }
        
        # Jeśli analiza związana z danymi studenckimi
        if any(word in query_text for word in ["student", "stypendi", "egzamin", "rekrutacj"]):
            # Zapytaj Agent1 o dane
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(
                        f"{AGENT1_URL}/api/chat",
                        json={
                            "messages": [
                                {"role": "user", "content": f"Podaj statystyki dla: {payload.input}"}
                            ],
                            "model": "mistral:7b",
                            "stream": False
                        }
                    )
                    
                    if response.status_code == 200:
                        agent1_data = response.json()
                        insights["data_from_agent1"] = agent1_data.get("message", {}).get("content", "")
                        insights["sources"] = agent1_data.get("sources", {})
                except Exception as e:
                    insights["agent1_error"] = str(e)
        
        return {
            "insights": insights,
            "input": payload.input
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agent": "agent3_analytics",
        "agent1_connection": AGENT1_URL
    }
