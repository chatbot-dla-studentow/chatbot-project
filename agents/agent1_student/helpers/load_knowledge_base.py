#!/usr/bin/env python3
"""
Skrypt do załadowania bazy wiedzy do Qdrant dla agent1_student
Wczytuje sparsowane dokumenty JSON z folderu knowledge
Używa Ollama embeddings (nomic-embed-text) - lekki model ~274MB, idealny dla 16GB RAM bez GPU
"""
import os
import json
import requests
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Konfiguracja
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
COLLECTION_NAME = "agent1_student"
KNOWLEDGE_BASE_PATH = "./knowledge"
EMBEDDING_MODEL = "nomic-embed-text"  # Lekki model embeddings dla Ollama (~274MB)

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

def load_json_documents(base_path: str) -> list:
    """Wczytuje wszystkie sparsowane dokumenty JSON z katalogu knowledge."""
    documents = []
    base_path = Path(base_path)
    
    # Wczytaj all_documents.json
    all_docs_path = base_path / "all_documents.json"
    if all_docs_path.exists():
        try:
            with open(all_docs_path, 'r', encoding='utf-8') as f:
                docs = json.load(f)
                for doc in docs:
                    documents.append({
                        "id": doc.get("id", ""),
                        "path": f"{doc.get('category', 'unknown')}/{doc.get('source_file', 'unknown')}",
                        "content": doc.get("content", ""),
                        "category": doc.get("category", "unknown"),
                        "metadata": doc.get("metadata", {})
                    })
            print(f"   Wczytano {len(documents)} dokumentów z all_documents.json")
        except Exception as e:
            print(f"   Błąd wczytywania all_documents.json: {e}")
    
    return documents

def create_collection(client: QdrantClient, vector_size: int):
    """Tworzy lub odtwarza kolekcję w Qdrant."""
    try:
        # Sprawdź czy kolekcja istnieje
        collections = client.get_collections().collections
        if any(c.name == COLLECTION_NAME for c in collections):
            print(f"Kolekcja '{COLLECTION_NAME}' już istnieje - usuwam i tworzę nową...")
            client.delete_collection(COLLECTION_NAME)
        
        # Utwórz nową kolekcję
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        print(f"Utworzono kolekcję '{COLLECTION_NAME}' (rozmiar wektora: {vector_size})")
    except Exception as e:
        print(f"Błąd tworzenia kolekcji: {e}")
        raise

def main():
    print("=" * 60)
    print("Ładowanie bazy wiedzy do Qdrant dla agent1_student")
    print("Używam Ollama embeddings (nomic-embed-text) - 16GB RAM friendly")
    print("=" * 60)
    
    # 1. Wczytaj sparsowane dokumenty JSON
    print(f"\n1. Wczytywanie dokumentów JSON z {KNOWLEDGE_BASE_PATH}...")
    documents = load_json_documents(KNOWLEDGE_BASE_PATH)
    print(f"   RAZEM: {len(documents)} dokumentów")
    
    if not documents:
        print("   BŁĄD: Nie znaleziono żadnych dokumentów!")
        return
    
    # 2. Sprawdź czy Ollama działa i pull model jeśli trzeba
    print(f"\n2. Sprawdzanie Ollama ({OLLAMA_URL})...")
    try:
        # Test connection
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        if response.status_code != 200:
            print(f"   BŁĄD: Ollama nie odpowiada!")
            return
        print("   Ollama działa!")
        
        # Sprawdź czy model jest dostępny
        print(f"   Sprawdzam model {EMBEDDING_MODEL}...")
        test_embedding = get_embedding("test")
        if not test_embedding:
            print(f"   Pobieram model {EMBEDDING_MODEL}...")
            pull_response = requests.post(
                f"{OLLAMA_URL}/api/pull",
                json={"name": EMBEDDING_MODEL},
                timeout=300
            )
            if pull_response.status_code == 200:
                print(f"   Model {EMBEDDING_MODEL} pobrany!")
                # Ponownie test
                test_embedding = get_embedding("test")
                if not test_embedding:
                    print(f"   BŁĄD: Model nie działa po pobraniu!")
                    return
            else:
                print(f"   BŁĄD pobierania modelu!")
                return
        
        vector_size = len(test_embedding)
        print(f"   Model {EMBEDDING_MODEL} gotowy (wymiar: {vector_size})")
    except Exception as e:
        print(f"   BŁĄD: {e}")
        return
    
    # 3. Połącz z Qdrant
    print(f"\n3. Łączenie z Qdrant ({QDRANT_HOST}:{QDRANT_PORT})...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    print("   Połączono!")
    
    # 4. Utwórz kolekcję
    print(f"\n4. Tworzenie kolekcji '{COLLECTION_NAME}'...")
    create_collection(client, vector_size)
    
    # 5. Generuj embeddingi i wstaw do Qdrant
    print(f"\n5. SZYBKIE ładowanie {len(documents)} dokumentów...")
    points = []
    missed = []
    batch_size = 20
    doc_id = 0
    
    for idx, doc in enumerate(documents):
        print(f"\r   {idx+1}/{len(documents)}", end="", flush=True)
        
        embedding = get_embedding(doc.get("content", ""), timeout=8)
        
        if embedding:
            points.append(PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "path": doc.get("path", ""),
                    "content": doc.get("content", ""),
                    "category": doc.get("category", ""),
                    "metadata": doc.get("metadata", {}),
                    "doc_id": doc.get("id", str(doc_id))
                }
            ))
            doc_id += 1
            
            # Batch insert
            if len(points) >= batch_size:
                client.upsert(collection_name=COLLECTION_NAME, points=points)
                points = []
        else:
            missed.append(doc.get("path", "unknown"))
    
    # Wstaw pozostałe
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
    
    # Zapisz pominięte
    if missed:
        missed_file = "./missed.txt"
        with open(missed_file, "w") as f:
            f.write("\n".join(missed))
        print(f"\nPominięto {len(missed)} dokumentów → {missed_file}")
    
    # 6. Statystyki
    print(f"\n\n6. Statystyki kolekcji:")
    collection_info = client.get_collection(COLLECTION_NAME)
    print(f"   - Liczba wektorów: {collection_info.points_count}")
    print(f"   - Wymiar wektora: {collection_info.config.params.vectors.size}")
    print(f"   - Metryka: {collection_info.config.params.vectors.distance}")
    
    # Przykładowe wyszukiwanie
    print(f"\n7. Test wyszukiwania:")
    test_queries = [
        "jak złożyć pracę dyplomową?",
        "jakie są stypendia dla studentów?",
        "jak zmienić kierunek studiów?"
    ]
    
    for test_query in test_queries:
        print(f"   Zapytanie: '{test_query}'")
        query_vector = get_embedding(test_query)
        
        if query_vector:
            results = client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=2
            )
            
            if results.points:
                for i, result in enumerate(results.points, 1):
                    print(f"      {i}. Kategoria: {result.payload.get('category', 'unknown')} (score: {result.score:.4f})")
                    content = result.payload.get('content', '')
                    print(f"         {content[:80]}...")
            else:
                print(f"      Brak wyników")
        print()
    
    print("=" * 60)
    print(f"Baza wiedzy załadowana pomyślnie!")
    print(f"   Załadowano {doc_id} dokumentów do kolekcji '{COLLECTION_NAME}'")
    print("=" * 60)

if __name__ == "__main__":
    main()
