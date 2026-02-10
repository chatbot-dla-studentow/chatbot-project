import os
import json
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from qdrant_client import QdrantClient
import httpx
from helpers.query_logger import QueryLogger

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

llm = ChatOllama(
    model="mistral:7b",
    base_url="http://ollama:11434"
)

COLLECTION = os.getenv("COLLECTION", "agent1_student")
NODERED_URL = os.getenv("NODERED_URL", "http://node-red:1880")
WORKFLOW_FILE = os.getenv("WORKFLOW_FILE", "/app/agent1_flow.json")
WORKFLOW_ENDPOINT = os.getenv("WORKFLOW_ENDPOINT", "/agent1_student")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
EMBEDDING_MODEL = "nomic-embed-text"  # Model embeddings w Ollama

# Inicjalizacja klientów
qdrant_client = None
embedding_model = None
query_logger = None

# Zmienna przechowująca status Node-RED
nodered_available = False


def load_workflow_json() -> dict:
    """Wczytuje workflow z pliku JSON."""
    workflow_path = Path(WORKFLOW_FILE)
    
    if not workflow_path.exists():
        raise RuntimeError(f"Plik workflow nie istnieje: {WORKFLOW_FILE}")
    
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        logger.info(f"Wczytano workflow z pliku: {WORKFLOW_FILE}")
        return workflow_data
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Błąd parsowania JSON w pliku {WORKFLOW_FILE}: {e}")
    except Exception as e:
        raise RuntimeError(f"Błąd wczytywania pliku workflow {WORKFLOW_FILE}: {e}")


def convert_bpmn_to_nodered(bpmn_data: dict) -> list:
    """Konwertuje pełny BPMN na Node-RED flows."""
    flows = []
    
    # Pobierz definicje BPMN
    definitions = bpmn_data.get("definitions", {})
    processes = definitions.get("process", [])
    if not isinstance(processes, list):
        processes = [processes]
    
    collaboration = definitions.get("collaboration", {})
    participants = collaboration.get("participant", [])
    if not isinstance(participants, list):
        participants = [participants]
    
    # Mapa procesów dla każdego uczestnika
    process_map = {}
    for process in processes:
        process_map[process.get("_id")] = process
    
    # Tworzenie flow dla każdego uczestnika
    y_offset = 0
    for participant in participants:
        participant_id = participant.get("_id")
        participant_name = participant.get("_name")
        process_ref = participant.get("_processRef")
        
        if not process_ref or process_ref not in process_map:
            continue
        
        process = process_map[process_ref]
        
        # Tworzenie zakładki (tab) dla uczestnika
        tab_id = f"tab_{participant_id}"
        tab = {
            "id": tab_id,
            "type": "tab",
            "label": participant_name or participant_id,
            "disabled": False
        }
        flows.append(tab)
        
        # HTTP IN endpoint dla głównego agenta
        if participant_name == "agent1_student":
            http_in = {
                "id": f"http_in_{participant_id}",
                "type": "http in",
                "z": tab_id,
                "name": f"{participant_name} Endpoint",
                "url": f"/{participant_name}",
                "method": "post",
                "upload": False,
                "x": 100,
                "y": 100 + y_offset,
                "wires": [[f"start_{participant_id}"]]
            }
            flows.append(http_in)
        
        # Start Event
        start_event = process.get("startEvent")
        if start_event:
            start_node = {
                "id": f"start_{participant_id}",
                "type": "function",
                "z": tab_id,
                "name": start_event.get("_name", "Start"),
                "func": "// Inicjalizacja procesu\nmsg.processData = msg.processData || {};\nmsg.processData.currentStep = 'started';\nreturn msg;",
                "outputs": 1,
                "x": 300,
                "y": 100 + y_offset,
                "wires": [[f"task_main_{participant_id}"]]
            }
            flows.append(start_node)
        
        # Service Tasks
        service_tasks = process.get("serviceTask", [])
        if not isinstance(service_tasks, list):
            service_tasks = [service_tasks]
        
        x_pos = 500
        for idx, task in enumerate(service_tasks[:3]):  # Pierwsze 3 taski
            task_id = task.get("_id")
            task_name = task.get("_name", f"Task {idx}")
            
            # Określ typ zadania
            if "Ollama" in task_name or "model" in task_name.lower():
                # Zapytanie do Ollama
                task_node = {
                    "id": f"task_{task_id}",
                    "type": "function",
                    "z": tab_id,
                    "name": task_name,
                    "func": f"// {task_name}\nconst input = msg.payload.message || msg.payload.input || msg.payload;\nmsg.payload = {{\n    model: 'mistral:7b',\n    prompt: input,\n    stream: false\n}};\nreturn msg;",
                    "outputs": 1,
                    "x": x_pos,
                    "y": 100 + y_offset + (idx * 80),
                    "wires": [[f"ollama_req_{participant_id}"]]
                }
            elif "qdrant" in task_name.lower() or "baz" in task_name.lower():
                # Wyszukiwanie w bazie
                task_node = {
                    "id": f"task_{task_id}",
                    "type": "http request",
                    "z": tab_id,
                    "name": task_name,
                    "method": "POST",
                    "ret": "obj",
                    "url": "http://qdrant:6333/collections/agent1_student/points/search",
                    "x": x_pos,
                    "y": 100 + y_offset + (idx * 80),
                    "wires": [[f"next_{participant_id}_{idx}"]]
                }
            else:
                # Ogólne zadanie
                task_node = {
                    "id": f"task_{task_id}",
                    "type": "function",
                    "z": tab_id,
                    "name": task_name,
                    "func": f"// {task_name}\nmsg.processData = msg.processData || {{}};\nmsg.processData.step = '{task_name}';\nreturn msg;",
                    "outputs": 1,
                    "x": x_pos,
                    "y": 100 + y_offset + (idx * 80),
                    "wires": [[f"next_{participant_id}_{idx}"]]
                }
            flows.append(task_node)
        
        # Główny task processing
        main_task = {
            "id": f"task_main_{participant_id}",
            "type": "function",
            "z": tab_id,
            "name": "Process Request",
            "func": "// Przetwarzanie zapytania\nconst input = msg.payload.message || msg.payload.input || msg.payload;\nmsg.payload = {\n    model: 'mistral:7b',\n    prompt: input,\n    stream: false\n};\nreturn msg;",
            "outputs": 1,
            "x": 500,
            "y": 100 + y_offset,
            "wires": [[f"ollama_req_{participant_id}"]]
        }
        flows.append(main_task)
        
        # Ollama Request
        ollama_req = {
            "id": f"ollama_req_{participant_id}",
            "type": "http request",
            "z": tab_id,
            "name": "Query Ollama",
            "method": "POST",
            "ret": "obj",
            "url": "http://ollama:11434/api/generate",
            "x": 700,
            "y": 100 + y_offset,
            "wires": [[f"format_{participant_id}"]]
        }
        flows.append(ollama_req)
        
        # Format Response
        format_resp = {
            "id": f"format_{participant_id}",
            "type": "function",
            "z": tab_id,
            "name": "Format Response",
            "func": f"msg.payload = {{\n    result: msg.payload.response || msg.payload,\n    agent: '{participant_name}',\n    collection: '{participant_name}'\n}};\nreturn msg;",
            "outputs": 1,
            "x": 900,
            "y": 100 + y_offset,
            "wires": [[f"gateway_{participant_id}"]]
        }
        flows.append(format_resp)
        
        # Gateway - decyzja
        gateways = process.get("exclusiveGateway", [])
        if not isinstance(gateways, list):
            gateways = [gateways] if gateways else []
        
        if gateways:
            gateway = gateways[0]
            gateway_name = gateway.get("_name", "Decision")
            gateway_node = {
                "id": f"gateway_{participant_id}",
                "type": "switch",
                "z": tab_id,
                "name": gateway_name,
                "property": "payload.needsMoreInfo",
                "rules": [
                    {"t": "true"},
                    {"t": "else"}
                ],
                "x": 1100,
                "y": 100 + y_offset,
                "wires": [
                    [f"more_info_{participant_id}"],
                    [f"http_resp_{participant_id}"]
                ]
            }
            flows.append(gateway_node)
            
            # More info node
            more_info = {
                "id": f"more_info_{participant_id}",
                "type": "function",
                "z": tab_id,
                "name": "Request More Info",
                "func": "msg.payload.message = 'Potrzebuję więcej informacji';\nreturn msg;",
                "outputs": 1,
                "x": 1100,
                "y": 200 + y_offset,
                "wires": [[f"http_resp_{participant_id}"]]
            }
            flows.append(more_info)
        
        # HTTP Response (tylko dla głównego agenta)
        if participant_name == "agent1_student":
            http_resp = {
                "id": f"http_resp_{participant_id}",
                "type": "http response",
                "z": tab_id,
                "name": "Send Response",
                "statusCode": "",
                "x": 1300,
                "y": 100 + y_offset,
                "wires": []
            }
            flows.append(http_resp)
        
        # Komunikacja z innymi agentami (MessageFlows)
        message_flows = collaboration.get("messageFlow", [])
        if not isinstance(message_flows, list):
            message_flows = [message_flows] if message_flows else []
        
        for msg_flow in message_flows:
            source_ref = msg_flow.get("_sourceRef")
            target_ref = msg_flow.get("_targetRef")
            
            # Znajdź target agent
            for other_participant in participants:
                other_process_ref = other_participant.get("_processRef")
                if other_process_ref and other_process_ref in process_map:
                    other_process = process_map[other_process_ref]
                    # Sprawdź czy source lub target należy do tego procesu
                    # (uproszczona implementacja)
                    pass
        
        y_offset += 400
    
    logger.info(f"Przekonwertowano pełny BPMN na {len(flows)} węzłów Node-RED ({len(participants)} uczestników)")
    return flows


async def publish_workflow_to_nodered(workflow_data: dict) -> bool:
    """Publikuje workflow do Node-RED przez Admin API."""
    global nodered_available
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Node-RED oczekuje tablicy flows, nie pojedynczego obiektu
            # Jeśli workflow_data jest obiektem BPMN, konwertujemy go
            if isinstance(workflow_data, dict) and "definitions" in workflow_data:
                logger.info("Wykryto format BPMN - konwertuję na Node-RED flows")
                flows = convert_bpmn_to_nodered(workflow_data)
            elif isinstance(workflow_data, list):
                flows = workflow_data
            else:
                flows = [workflow_data]
            
            # Próba opublikowania workflow do Node-RED Admin API
            response = await client.post(
                f"{NODERED_URL}/flows",
                json=flows,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 204]:
                logger.info("Workflow został opublikowany do Node-RED")
                nodered_available = True
                return True
            else:
                logger.warning(
                    f"Node-RED odpowiedział kodem {response.status_code}: {response.text}"
                )
                nodered_available = False
                return False
                
    except httpx.ConnectError:
        logger.warning(
            f"Nie można połączyć z Node-RED pod adresem {NODERED_URL}. "
            "Endpoint /run będzie zwracał 503 do czasu nawiązania połączenia."
        )
        nodered_available = False
        return False
    except Exception as e:
        logger.warning(f"Błąd podczas publikacji workflow do Node-RED: {e}")
        nodered_available = False
        return False


@app.on_event("startup")
async def startup_event():
    """Event wykonywany przy starcie aplikacji."""
    logger.info("Uruchamianie aplikacji agent1_student...")
    
    # Automatyczne publikowanie BPMN wyłączone - powoduje problemy
    # Workflow można opublikować ręcznie przez endpoint /publish-workflow
    # workflow_data = load_workflow_json()
    # await publish_workflow_to_nodered(workflow_data)
    
    # Inicjalizacja Qdrant i embeddings
    global qdrant_client, embedding_model, query_logger
    try:
        logger.info(f"Inicjalizacja Qdrant client ({QDRANT_HOST}:{QDRANT_PORT})...")
        qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        logger.info("Qdrant client zainicjalizowany")
        
        logger.info(f"Ładowanie modelu embeddings: {EMBEDDING_MODEL}...")
        embedding_model = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url="http://ollama:11434"
        )
        logger.info("Model embeddings załadowany")
        
        # Inicjalizacja QueryLogger
        logger.info("Inicjalizacja QueryLogger...")
        query_logger = QueryLogger(
            qdrant_client=qdrant_client,
            embedding_func=lambda text: embedding_model.embed_query(text)
        )
        logger.info("QueryLogger zainicjalizowany pomyślnie")
        
    except Exception as e:
        logger.error(f"Błąd podczas inicjalizacji: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
        
    except Exception as e:
        logger.error(f"Błąd inicjalizacji RAG: {e}")
        # Nie przerywamy startu aplikacji - RAG jest opcjonalny


def search_knowledge_base(query: str, limit: int = 3) -> list:
    """Wyszukuje dokumenty w bazie wiedzy."""
    try:
        if not qdrant_client or not embedding_model:
            return []
        
        # Generuj embedding zapytania
        query_vector = embedding_model.embed_query(query)
        
        # Wyszukaj w Qdrant
        results = qdrant_client.query_points(
            collection_name=COLLECTION,
            query=query_vector,
            limit=limit
        )
        
        # Wyciągnij dokumenty z wyników
        documents = []
        for result in results.points:
            documents.append({
                "content": result.payload.get("content", ""),
                "path": result.payload.get("path", ""),
                "category": result.payload.get("category", ""),
                "score": result.score
            })
        
        return documents
    except Exception as e:
        logger.error(f"Błąd wyszukiwania w bazie wiedzy: {e}")
        return []


@app.post("/run")
async def run(payload: dict):
    """Endpoint przekazujący zapytania do Node-RED workflow."""
    global nodered_available
    
    # Sprawdzenie dostępności Node-RED
    if not nodered_available:
        raise HTTPException(
            status_code=503,
            detail="Node-RED jest niedostępny. Spróbuj ponownie później."
        )
    
    try:
        # Wzbogacenie zapytania o kontekst z bazy wiedzy (RAG)
        user_query = payload.get("message", "")
        if user_query:
            # Wyszukaj w bazie wiedzy
            knowledge_docs = search_knowledge_base(user_query)
            
            if knowledge_docs:
                # Wzbogać message o kontekst (skrócony do 100 znaków na dokument)
                context = "\n".join([
                    f"{doc['content'][:100]}..."
                    for doc in knowledge_docs[:1]  # Tylko najlepszy dokument
                ])
                enriched_message = f"Info: {context}\n\nQ: {user_query}"
                payload["message"] = enriched_message
                logger.info(f"Znaleziono {len(knowledge_docs)} dokumentów w bazie wiedzy")
            else:
                # Brak dokumentów - dodaj informację
                payload["message"] = f"Brak informacji na ten temat w bazie wiedzy.\n\nPytanie użytkownika: {user_query}"
                logger.info("Nie znaleziono dokumentów w bazie wiedzy")
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Forwardowanie zapytania do Node-RED workflow
            response = await client.post(
                f"{NODERED_URL}{WORKFLOW_ENDPOINT}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Jeśli Node-RED zwrócił błąd 4xx lub 5xx
            if response.status_code >= 400:
                logger.error(
                    f"Node-RED zwrócił błąd {response.status_code}: {response.text}"
                )
                raise HTTPException(
                    status_code=502,
                    detail=f"Node-RED error: {response.text}"
                )
            
            # Zwrócenie odpowiedzi z Node-RED
            return response.json()
            
    except httpx.ConnectError:
        nodered_available = False
        logger.error(f"Nie można połączyć z Node-RED: {NODERED_URL}{WORKFLOW_ENDPOINT}")
        raise HTTPException(
            status_code=503,
            detail="Nie można połączyć z Node-RED"
        )
    except httpx.TimeoutException:
        logger.error(f"Timeout podczas połączenia z Node-RED")
        raise HTTPException(
            status_code=503,
            detail="Timeout podczas komunikacji z Node-RED"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd podczas komunikacji z Node-RED: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Błąd podczas komunikacji z Node-RED: {str(e)}"
        )


@app.post("/publish-workflow")
async def publish_workflow_endpoint():
    """Endpoint do ręcznej publikacji workflow BPMN do Node-RED."""
    try:
        # Wczytaj workflow z pliku
        workflow_data = load_workflow_json()
        
        # Opublikuj do Node-RED
        success = await publish_workflow_to_nodered(workflow_data)
        
        if success:
            return {
                "status": "success",
                "message": "Workflow został opublikowany do Node-RED"
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="Nie udało się opublikować workflow do Node-RED"
            )
    except Exception as e:
        logger.error(f"Błąd podczas publikowania workflow: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Błąd: {str(e)}"
        )


@app.post("/api/generate")
async def ollama_generate_with_rag(payload: dict):
    """
    Endpoint kompatybilny z Ollama API, wzbogacony o RAG.
    Open WebUI może używać tego endpointu zamiast bezpośredniego Ollama.
    """
    try:
        # Wyciągnij prompt z zapytania
        prompt = payload.get("prompt", "")
        model = payload.get("model", "mistral:7b")
        stream = payload.get("stream", False)
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Brak prompt w zapytaniu")
        
        # Wyszukaj w bazie wiedzy
        enriched_prompt = prompt
        if qdrant_client and embedding_model:
            try:
                knowledge_docs = search_knowledge_base(prompt)
                
                if knowledge_docs:
                    # Minimalny kontekst dla szybkości (1 dokument, 80 znaków)
                    context = knowledge_docs[0]['content'][:80]
                    enriched_prompt = f"{context}...\n\n{prompt}"
                    logger.info(f"RAG: Użyto kontekstu")
                else:
                    logger.info("RAG: Brak dokumentów")
            except Exception as e:
                logger.error(f"RAG error: {e}")
        
        # Przekaż do Ollama z maksymalną optymalizacją szybkości
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": model,
                    "prompt": enriched_prompt,
                    "stream": stream,
                    "options": {
                        "num_predict": 50,      # Max 50 tokenów - SZYBKO
                        "temperature": 0.5,      # Mniej losowości
                        "top_k": 20,            # Ograniczenie wyboru
                        "num_ctx": 512,         # Mniejsze context window
                    }
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ollama error: {response.text}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd w /api/generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tags")
async def ollama_tags():
    """Proxy do Ollama /api/tags - lista modeli."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("http://ollama:11434/api/tags")
            return response.json()
    except Exception as e:
        logger.error(f"Błąd w /api/tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/version")
async def ollama_version():
    """Proxy do Ollama /api/version."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("http://ollama:11434/api/version")
            return response.json()
    except Exception as e:
        return {"version": "0.1.0-rag-proxy"}


@app.post("/api/chat")
async def ollama_chat_with_rag(payload: dict):
    """
    Endpoint /api/chat kompatybilny z Ollama API, wzbogacony o RAG.
    Open WebUI używa tego endpointu do konwersacji.
    ROZSZERZONY: Loguje zapytania i odpowiedzi do Qdrant.
    """
    try:
        # Wyciągnij ostatnią wiadomość z konwersacji
        messages = payload.get("messages", [])
        model = payload.get("model", "mistral:7b")
        stream = payload.get("stream", False)
        
        if not messages:
            raise HTTPException(status_code=400, detail="Brak messages w zapytaniu")
        
        # Pobierz ostatnią wiadomość użytkownika
        last_message = messages[-1].get("content", "") if messages else ""
        
        # LOGOWANIE ZAPYTANIA
        detected_category = None
        rag_score = None
        sources_list = []
        
        if query_logger:
            detected_category = query_logger.detect_category(last_message)
            query_logger.log_query(
                query=last_message,
                category=detected_category,
                metadata={"model": model}
            )
        
        # Wyszukaj w bazie wiedzy
        enriched_messages = messages.copy()
        if qdrant_client and embedding_model and last_message:
            try:
                knowledge_docs = search_knowledge_base(last_message, limit=2)
                
                if knowledge_docs and knowledge_docs[0]['score'] > 0.25:
                    # Zbierz kontekst z najlepszych wyników
                    contexts = []
                    for doc in knowledge_docs[:2]:
                        if doc['score'] > 0.25:
                            # Weź pierwszych 600 znaków
                            contexts.append(doc['content'][:600])
                            sources_list.append(doc.get('path', 'unknown'))
                    
                    context_text = "\n---\n".join(contexts)
                    rag_score = knowledge_docs[0]['score']
                    
                    # Wstaw kontekst BEZPOŚREDNIO do ostatniej wiadomości użytkownika
                    enriched_last_msg = f"""KONTEKST Z BAZY WIEDZY:
{context_text}

---

PYTANIE UŻYTKOWNIKA: {last_message}

Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, napisz: "Nie mam tej informacji w bazie wiedzy"."""
                    
                    # Zamień ostatnią wiadomość na wzbogaconą
                    enriched_messages[-1]["content"] = enriched_last_msg
                    logger.info(f"RAG: Found {len(contexts)} docs (score: {knowledge_docs[0]['score']:.3f})")
                else:
                    logger.info(f"RAG: No good results (best score: {knowledge_docs[0]['score'] if knowledge_docs else 0:.3f})")
            except Exception as e:
                logger.error(f"RAG error w chat: {e}")
        
        # Przekaż do Ollama
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://ollama:11434/api/chat",
                json={
                    "model": model,
                    "messages": enriched_messages,
                    "stream": stream,
                    "options": {
                        "num_predict": 80,       # Krótsze odpowiedzi
                        "temperature": 0.3,      # Mniej losowości
                        "top_k": 10,            # Bardziej skoncentrowany wybór
                        "num_ctx": 1024,        # Mniej kontekstu
                    }
                }
            )
            
            if stream:
                # Zwróć streaming response
                from fastapi.responses import StreamingResponse
                return StreamingResponse(
                    response.iter_bytes(),
                    media_type="application/x-ndjson"
                )
            else:
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # LOGOWANIE ODPOWIEDZI (QA PAIR)
                    if query_logger and not stream:
                        answer = response_data.get("message", {}).get("content", "")
                        if answer:
                            query_logger.log_qa_pair(
                                query=last_message,
                                answer=answer,
                                category=detected_category,
                                sources=sources_list,
                                score=rag_score,
                                metadata={"model": model}
                            )
                    
                    # Dodaj sources do odpowiedzi (dla frontend)
                    if sources_list and rag_score:
                        response_data["sources"] = {
                            "documents": sources_list,
                            "score": round(rag_score, 3),
                            "category": detected_category
                        }
                    
                    return response_data
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Ollama error: {response.text}"
                    )
                
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Błąd w /api/chat: {e}")
        logger.error(f"Traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ps")
async def ollama_ps():
    """
    Endpoint /api/ps - lista uruchomionych modeli.
    Zwraca pustą listę lub proxy do Ollama.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://ollama:11434/api/ps")
            if response.status_code == 200:
                return response.json()
            else:
                # Jeśli Ollama nie ma tego endpointu, zwróć pustą listę
                return {"models": []}
    except Exception as e:
        logger.error(f"Błąd w /api/ps: {e}")
        return {"models": []}


# Endpointy dla Open WebUI (używa /ollama/ prefix)
@app.post("/ollama/api/generate")
async def ollama_generate_webui(payload: dict):
    """Endpoint dla Open WebUI z prefixem /ollama/."""
    return await ollama_generate_with_rag(payload)


@app.get("/ollama/api/tags")
async def ollama_tags_webui():
    """Endpoint dla Open WebUI z prefixem /ollama/."""
    return await ollama_tags()


@app.get("/ollama/api/version")
async def ollama_version_webui():
    """Endpoint dla Open WebUI z prefixem /ollama/."""
    return await ollama_version()


@app.post("/api/pull")
async def ollama_pull(payload: dict):
    """
    Endpoint /api/pull - pobieranie modelu z Ollama.
    Proxy do Ollama dla Open WebUI.
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                "http://ollama:11434/api/pull",
                json=payload
            )
            
            if payload.get("stream", False):
                from fastapi.responses import StreamingResponse
                return StreamingResponse(
                    response.iter_bytes(),
                    media_type="application/x-ndjson"
                )
            else:
                return response.json()
    except Exception as e:
        logger.error(f"Błąd w /api/pull: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ollama/api/pull")
async def ollama_pull_webui(payload: dict):
    """Endpoint dla Open WebUI z prefixem /ollama/."""
    return await ollama_pull(payload)


@app.post("/api/push")
async def ollama_push(payload: dict):
    """Endpoint /api/push - publikowanie modelu."""
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                "http://ollama:11434/api/push",
                json=payload
            )
            
            if payload.get("stream", False):
                from fastapi.responses import StreamingResponse
                return StreamingResponse(
                    response.iter_bytes(),
                    media_type="application/x-ndjson"
                )
            else:
                return response.json()
    except Exception as e:
        logger.error(f"Błąd w /api/push: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/delete")
async def ollama_delete(payload: dict):
    """Endpoint /api/delete - usuwanie modelu."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                "http://ollama:11434/api/delete",
                json=payload
            )
            return response.json()
    except Exception as e:
        logger.error(f"Błąd w /api/delete: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTY ADMINISTRACYJNE DLA LOGÓW
# ============================================================================

@app.get("/admin/logs/queries/stats")
async def get_query_stats_endpoint():
    """
    Endpoint do pobierania statystyk zapytań.
    
    Returns:
        Statystyki zapytań (liczba, kategorie, etc.)
    """
    try:
        if not query_logger:
            raise HTTPException(status_code=503, detail="QueryLogger nie został zainicjalizowany")
        
        stats = query_logger.get_query_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Błąd w /admin/logs/queries/stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/logs/qa/stats")
async def get_qa_stats_endpoint():
    """
    Endpoint do pobierania statystyk par pytanie-odpowiedź.
    
    Returns:
        Statystyki QA (liczba, kategorie, średni score, etc.)
    """
    try:
        if not query_logger:
            raise HTTPException(status_code=503, detail="QueryLogger nie został zainicjalizowany")
        
        stats = query_logger.get_qa_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Błąd w /admin/logs/qa/stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/logs/queries/search")
async def search_similar_queries_endpoint(query: str, limit: int = 10):
    """
    Endpoint do wyszukiwania podobnych zapytań w historii.
    
    Query params:
        query: Zapytanie do wyszukania
        limit: Maksymalna liczba wyników (domyślnie 10)
    
    Returns:
        Lista podobnych zapytań z score
    """
    try:
        if not query_logger:
            raise HTTPException(status_code=503, detail="QueryLogger nie został zainicjalizowany")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        similar_queries = query_logger.search_similar_queries(query, limit=limit)
        return {
            "success": True,
            "query": query,
            "count": len(similar_queries),
            "results": similar_queries
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd w /admin/logs/queries/search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/logs/categories")
async def get_categories_endpoint():
    """
    Endpoint zwracający listę dostępnych kategorii.
    
    Returns:
        Lista kategorii z opisami
    """
    try:
        from query_logger import CATEGORIES
        
        categories_info = []
        for cat_id, keywords in CATEGORIES.items():
            categories_info.append({
                "id": cat_id,
                "keywords_count": len(keywords),
                "keywords": keywords
            })
        
        return {
            "success": True,
            "count": len(categories_info),
            "categories": categories_info
        }
    except Exception as e:
        logger.error(f"Błąd w /admin/logs/categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
