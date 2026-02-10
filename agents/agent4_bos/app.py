"""Agent 4 - BOS (Biuro Obsługi Studenta)
Agent BOS - komunikuje się z Agent1 Student dla procedur BOS
"""
import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

# Konfiguracja
AGENT1_URL = os.getenv("AGENT1_URL", "http://agent1_student:8001")

app = FastAPI(title="Agent 4 - BOS")

class BOSRequest(BaseModel):
    input: str
    user_id: Optional[str] = "anonymous"
    metadata: Optional[Dict] = {}

@app.post("/run")
async def process_bos_request(payload: BOSRequest):
    """
    Przetwarza zapytanie BOS.
    Komunikuje się z Agent1 dla wiedzy o procedurach BOS.
    """
    try:
        # BOS zawsze korzysta z Agent1 dla wiedzy
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{AGENT1_URL}/api/chat",
                    json={
                        "messages": [
                            {"role": "user", "content": payload.input}
                        ],
                        "model": "mistral:7b",
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    agent1_data = response.json()
                    return {
                        "draft": agent1_data.get("message", {}).get("content", ""),
                        "sources": agent1_data.get("sources", {}),
                        "agent": "agent4_bos",
                        "input": payload.input
                    }
                else:
                    raise HTTPException(status_code=response.status_code, detail="Agent1 error")
                    
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Agent1 timeout")
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "agent": "agent4_bos",
        "agent1_connection": AGENT1_URL
    }
