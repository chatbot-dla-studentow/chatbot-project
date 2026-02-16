#!/usr/bin/env python3
"""
Skrypt do inkrementalnej aktualizacji bazy wiedzy w Qdrant.
Dodaje tylko nowe dokumenty bez usuwania istniejących.
"""
import os
import json
import hashlib
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import requests

# Konfiguracja
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
COLLECTION_NAME = "agent1_student"
KNOWLEDGE_BASE_PATH = "./knowledge"
EMBEDDING_MODEL = "nomic-embed-text"

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

def calculate_document_hash(doc: dict) -> str:
    """Oblicza MD5 hash dokumentu (na podstawie content + path)."""
    content = doc.get("content", "")
    path = doc.get("path", "")
    combined = f"{path}||{content}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def get_existing_documents(client: QdrantClient) -> dict:
    """
    Pobiera wszystkie istniejące dokumenty z Qdrant.
    Zwraca dict: {hash: doc_id}
    """
    print("Pobieranie istniejących dokumentów z Qdrant...")
    existing = {}
    
    try:
        # Scroll przez wszystkie punkty
        offset = None
        total_fetched = 0
        
        while True:
            result = client.scroll(
                collection_name=COLLECTION_NAME,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            points, offset = result
            
            if not points:
                break
            
            for point in points:
                # Oblicz hash z payload
                doc_data = {
                    "content": point.payload.get("content", ""),
                    "path": point.payload.get("path", "")
                }
                doc_hash = calculate_document_hash(doc_data)
                existing[doc_hash] = point.id
            
            total_fetched += len(points)
            print(f"   Pobrano: {total_fetched} dokumentów...", end='\r')
            
            if offset is None:
                break
        
        print(f"\n   Znaleziono {len(existing)} unikalnych dokumentów w Qdrant")
        return existing
        
    except Exception as e:
        print(f"Błąd pobierania dokumentów: {e}")
        return {}

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

def main():
    print("=" * 70)
    print("Inkrementalna Aktualizacja Bazy Wiedzy")
    print("Dodaje tylko nowe dokumenty bez usuwania istniejących")
    print("=" * 70)
    
    # 1. Wczytaj dokumenty JSON
    print(f"\n1. Wczytywanie dokumentów JSON z {KNOWLEDGE_BASE_PATH}...")
    all_documents = load_json_documents(KNOWLEDGE_BASE_PATH)
    
    if not all_documents:
        print("   BŁĄD: Nie znaleziono żadnych dokumentów!")
        return
    
    print(f"   RAZEM: {len(all_documents)} dokumentów do sprawdzenia")
    
    # 2. Sprawdź Ollama
    print(f"\n2. Sprawdzanie Ollama ({OLLAMA_URL})...")
    try:
        test_embedding = get_embedding("test")
        if not test_embedding:
            print("   BŁĄD: Nie można uzyskać embeddingu z Ollama")
            return
        
        vector_size = len(test_embedding)
        print(f"   Model {EMBEDDING_MODEL} gotowy (wymiar: {vector_size})")
    except Exception as e:
        print(f"   BŁĄD: {e}")
        return
    
    # 3. Połącz z Qdrant
    print(f"\n3. Łączenie z Qdrant ({QDRANT_HOST}:{QDRANT_PORT})...")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Sprawdź czy kolekcja istnieje
        collections = client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            print(f"   BŁĄD: Kolekcja '{COLLECTION_NAME}' nie istnieje!")
            print(f"   Użyj najpierw 'load_knowledge_base.py' aby stworzyć kolekcję.")
            return
        
        print(f"   Połączono z kolekcją '{COLLECTION_NAME}'")
    except Exception as e:
        print(f"   BŁĄD: {e}")
        return
    
    # 4. Pobierz istniejące dokumenty
    print(f"\n4. Pobieranie istniejących dokumentów...")
    existing_hashes = get_existing_documents(client)
    
    # 5. Filtruj nowe dokumenty
    print(f"\n5. Filtrowanie nowych dokumentów...")
    new_documents = []
    skipped_count = 0
    
    for doc in all_documents:
        doc_hash = calculate_document_hash(doc)
        
        if doc_hash in existing_hashes:
            # Dokument już istnieje - pomiń
            skipped_count += 1
        else:
            # Nowy dokument - dodaj do listy
            new_documents.append(doc)
    
    print(f"   Znaleziono {len(new_documents)} nowych dokumentów")
    print(f"   Pominięto {skipped_count} istniejących dokumentów")
    
    if not new_documents:
        print("\nBaza wiedzy jest aktualna - brak nowych dokumentów do dodania!")
        return
    
    # 6. Dodaj nowe dokumenty
    print(f"\n6. Dodawanie {len(new_documents)} nowych dokumentów do Qdrant...")
    
    added_count = 0
    failed_count = 0
    
    for idx, doc in enumerate(new_documents, 1):
        try:
            # Generuj embedding
            embedding = get_embedding(doc["content"])
            if not embedding:
                print(f"   Błąd embeddingu dla dokumentu {idx}/{len(new_documents)}")
                failed_count += 1
                continue
            
            # Przygotuj punkt
            point = PointStruct(
                id=doc["id"],
                vector=embedding,
                payload={
                    "content": doc["content"],
                    "path": doc["path"],
                    "category": doc["category"],
                    "metadata": doc["metadata"]
                }
            )
            
            # Dodaj do Qdrant (upsert - nadpisuje jeśli ID istnieje)
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=[point]
            )
            
            added_count += 1
            
            # Progress bar
            if idx % 10 == 0 or idx == len(new_documents):
                progress = (idx / len(new_documents)) * 100
                print(f"   Postęp: {idx}/{len(new_documents)} ({progress:.1f}%) - dodano: {added_count}, błędy: {failed_count}", end='\r')
        
        except Exception as e:
            print(f"\n   Błąd dodawania dokumentu {idx}: {e}")
            failed_count += 1
    
    print()  # Nowa linia po progress bar
    
    # 7. Podsumowanie
    print("\n" + "=" * 70)
    print("PODSUMOWANIE AKTUALIZACJI")
    print("=" * 70)
    print(f"Dokumenty w JSON:           {len(all_documents)}")
    print(f"Istniejące w Qdrant:        {len(existing_hashes)}")
    print(f"Nowe do dodania:            {len(new_documents)}")
    print(f"Pomyślnie dodane:         {added_count}")
    print(f"Błędy:                    {failed_count}")
    
    # Sprawdź finalny stan kolekcji
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"\nAktualny stan kolekcji:     {collection_info.points_count} punktów")
    except:
        pass
    
    print("=" * 70)
    
    if failed_count > 0:
        print(f"\n️  UWAGA: {failed_count} dokumentów nie zostało dodanych z powodu błędów")
    else:
        print("\nAktualizacja zakończona sukcesem!")

if __name__ == "__main__":
    main()
