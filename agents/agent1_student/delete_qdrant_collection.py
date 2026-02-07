#!/usr/bin/env python3
"""
Skrypt do usunięcia kolekcji z Qdrant
Uruchom ten skrypt w kontenerze dockera lub zmień QDRANT_HOST na localhost:6333
"""
import os
from qdrant_client import QdrantClient

# Konfiguracja
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")  # zmienione na localhost
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "agent1_student"

def delete_collection():
    """Usuwa kolekcję z Qdrant"""
    try:
        print(f"Łączenie z Qdrant ({QDRANT_HOST}:{QDRANT_PORT})...")
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        print("Połączono!")
        
        # Sprawdź czy kolekcja istnieje
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        print(f"\nDostępne kolekcje: {', '.join(collection_names) if collection_names else 'brak'}")
        
        if COLLECTION_NAME in collection_names:
            print(f"\nUsuwam kolekcję '{COLLECTION_NAME}'...")
            client.delete_collection(COLLECTION_NAME)
            print(f"✓ Kolekcja '{COLLECTION_NAME}' została usunięta!")
        else:
            print(f"\n⚠ Kolekcja '{COLLECTION_NAME}' nie istnieje - nic do usunięcia")
        
        # Pokaż pozostałe kolekcje
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        print(f"\nPozostałe kolekcje: {', '.join(collection_names) if collection_names else 'brak'}")
        
    except Exception as e:
        print(f"✗ Błąd: {e}")

if __name__ == "__main__":
    delete_collection()
