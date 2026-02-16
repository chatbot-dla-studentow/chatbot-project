#!/usr/bin/env python3
"""
Skrypt do inicjalizacji kolekcji logów w Qdrant dla Agent_1
- query_logs: logi zapytań użytkowników
- qa_logs: logi par pytanie-odpowiedź
"""
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import requests

# Konfiguracja
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = "nomic-embed-text"

COLLECTIONS = {
    "agent1_query_logs": "Logi zapytań użytkowników",
    "agent1_qa_logs": "Logi par pytanie-odpowiedź"
}

def get_embedding(text: str, timeout: int = 20) -> list:
    """Generuje embedding używając Ollama API."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=timeout
        )
        return response.json()["embedding"] if response.status_code == 200 else None
    except:
        return None

def create_log_collections(client: QdrantClient, vector_size: int):
    """Tworzy kolekcje dla logów w Qdrant."""
    
    for collection_name, description in COLLECTIONS.items():
        try:
            # Sprawdź czy kolekcja istnieje
            collections = client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                print(f"️  Kolekcja '{collection_name}' już istnieje - pomijam")
                continue
            
            # Utwórz nową kolekcję
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"Utworzono kolekcję '{collection_name}' - {description}")
            
        except Exception as e:
            print(f"Błąd tworzenia kolekcji {collection_name}: {e}")

def main():
    print("=" * 70)
    print("Inicjalizacja kolekcji logów dla Agent_1")
    print("=" * 70)
    
    # 1. Sprawdź Ollama i pobierz wymiar wektora
    print(f"\n1. Sprawdzanie Ollama ({OLLAMA_URL})...")
    try:
        test_embedding = get_embedding("test")
        if not test_embedding:
            print("Błąd: Nie można uzyskać embeddingu z Ollama")
            return
        
        vector_size = len(test_embedding)
        print(f"Model {EMBEDDING_MODEL} gotowy (wymiar: {vector_size})")
    except Exception as e:
        print(f"Błąd: {e}")
        return
    
    # 2. Połącz z Qdrant
    print(f"\n2. Łączenie z Qdrant ({QDRANT_HOST}:{QDRANT_PORT})...")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        print("Połączono!")
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        return
    
    # 3. Utwórz kolekcje
    print(f"\n3. Tworzenie kolekcji logów...")
    create_log_collections(client, vector_size)
    
    # 4. Podsumowanie
    print(f"\n4. Podsumowanie:")
    collections = client.get_collections().collections
    for collection_name in COLLECTIONS.keys():
        if any(c.name == collection_name for c in collections):
            info = client.get_collection(collection_name)
            print(f"   {collection_name}: {info.points_count} punktów")
        else:
            print(f"   {collection_name}: nie utworzono")
    
    print("\n" + "=" * 70)
    print("Inicjalizacja zakończona!")
    print("=" * 70)

if __name__ == "__main__":
    main()
