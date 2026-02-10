#!/usr/bin/env python3
"""
Skrypt do sprawdzania jakości danych w bazie wiedzy Qdrant.
Sprawdza duplikaty, kategoryzację, statystyki.
"""

import os
from collections import Counter, defaultdict
from pathlib import Path
from qdrant_client import QdrantClient
import hashlib

# Konfiguracja
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION = "agent1_student"
KNOWLEDGE_DIR = Path("chatbot-baza-wiedzy-nowa")

def analyze_qdrant_collection():
    """Analiza kolekcji w Qdrant."""
    print("=" * 80)
    print("ANALIZA BAZY WIEDZY W QDRANT")
    print("=" * 80)
    
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    try:
        # Informacje o kolekcji
        collection_info = client.get_collection(COLLECTION)
        print(f"\n📊 Kolekcja: {COLLECTION}")
        print(f"   Liczba punktów: {collection_info.points_count}")
        print(f"   Status: {collection_info.status}")
        
        # Pobierz wszystkie punkty
        scroll_result = client.scroll(
            collection_name=COLLECTION,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        
        points = scroll_result[0]
        print(f"\n📦 Pobrano {len(points)} dokumentów z Qdrant")
        
        if not points:
            print("\n⚠️  Brak dokumentów w kolekcji!")
            return
        
        # Analiza kategorii
        categories = [p.payload.get('category', 'BRAK KATEGORII') for p in points]
        category_counts = Counter(categories)
        
        print(f"\n📂 Kategorie dokumentów:")
        for category, count in category_counts.most_common():
            print(f"   {category}: {count} dokumentów")
        
        # Analiza ścieżek plików
        paths = [p.payload.get('path', 'BRAK ŚCIEŻKI') for p in points]
        path_counts = Counter(paths)
        
        print(f"\n📁 Źródła dokumentów (top 10):")
        for path, count in path_counts.most_common(10):
            filename = Path(path).name if path != 'BRAK ŚCIEŻKI' else path
            print(f"   {filename}: {count}x")
        
        # Sprawdzenie duplikatów po treści
        content_hashes = defaultdict(list)
        for p in points:
            content = p.payload.get('content', '')
            if content:
                content_hash = hashlib.md5(content.encode()).hexdigest()
                content_hashes[content_hash].append({
                    'id': p.id,
                    'path': p.payload.get('path', 'BRAK'),
                    'category': p.payload.get('category', 'BRAK'),
                    'preview': content[:100]
                })
        
        # Znajdź duplikaty
        duplicates = {h: docs for h, docs in content_hashes.items() if len(docs) > 1}
        
        if duplicates:
            print(f"\n❌ DUPLIKATY TREŚCI ({len(duplicates)} grup):")
            for idx, (hash_val, docs) in enumerate(duplicates.items(), 1):
                print(f"\n   Duplikat #{idx} ({len(docs)} kopii):")
                for doc in docs:
                    print(f"      - ID: {doc['id']}")
                    print(f"        Kategoria: {doc['category']}")
                    print(f"        Plik: {Path(doc['path']).name}")
                    print(f"        Podgląd: {doc['preview']}...")
        else:
            print(f"\n✅ Brak duplikatów treści!")
        
        # Analiza długości dokumentów
        content_lengths = [len(p.payload.get('content', '')) for p in points]
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        min_length = min(content_lengths) if content_lengths else 0
        max_length = max(content_lengths) if content_lengths else 0
        
        print(f"\n📏 Statystyki długości dokumentów:")
        print(f"   Średnia długość: {avg_length:.0f} znaków")
        print(f"   Min: {min_length} znaków")
        print(f"   Max: {max_length} znaków")
        
        # Dokumenty bardzo krótkie (podejrzane)
        short_docs = [(p.payload.get('path', 'BRAK'), len(p.payload.get('content', ''))) 
                      for p in points if len(p.payload.get('content', '')) < 50]
        
        if short_docs:
            print(f"\n⚠️  Bardzo krótkie dokumenty (< 50 znaków):")
            for path, length in short_docs:
                print(f"   {Path(path).name}: {length} znaków")
        
        # Przykładowe dokumenty z każdej kategorii
        print(f"\n📄 Przykładowe dokumenty z każdej kategorii:")
        for category in set(categories):
            sample = next((p for p in points if p.payload.get('category') == category), None)
            if sample:
                content_preview = sample.payload.get('content', '')[:200]
                print(f"\n   Kategoria: {category}")
                print(f"   Plik: {Path(sample.payload.get('path', 'BRAK')).name}")
                print(f"   Podgląd: {content_preview}...")
        
    except Exception as e:
        print(f"\n❌ Błąd podczas analizy Qdrant: {e}")
        import traceback
        traceback.print_exc()


def analyze_filesystem():
    """Analiza plików w systemie plików."""
    print("\n" + "=" * 80)
    print("ANALIZA PLIKÓW W FOLDERZE chatbot-baza-wiedzy-nowa")
    print("=" * 80)
    
    if not KNOWLEDGE_DIR.exists():
        print(f"\n❌ Folder {KNOWLEDGE_DIR} nie istnieje!")
        return
    
    # Znajdź wszystkie pliki .txt
    txt_files = list(KNOWLEDGE_DIR.rglob("*.txt"))
    
    print(f"\n📁 Znaleziono {len(txt_files)} plików .txt")
    
    # Grupuj po kategoriach (subfoldery)
    categories = defaultdict(list)
    for file in txt_files:
        # Kategoria = pierwszy subfolder po chatbot-baza-wiedzy-nowa
        parts = file.relative_to(KNOWLEDGE_DIR).parts
        category = parts[0] if len(parts) > 1 else "ROOT"
        categories[category].append(file)
    
    print(f"\n📂 Kategorie w systemie plików:")
    for category, files in sorted(categories.items()):
        print(f"   {category}: {len(files)} plików")
        for file in sorted(files):
            print(f"      - {file.name}")
    
    # Sprawdź duplikaty nazw plików
    filenames = [f.name for f in txt_files]
    filename_counts = Counter(filenames)
    duplicates = {name: count for name, count in filename_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n❌ DUPLIKATY NAZW PLIKÓW:")
        for name, count in duplicates.items():
            print(f"   {name}: {count}x")
            # Pokaż pełne ścieżki
            matching_files = [f for f in txt_files if f.name == name]
            for f in matching_files:
                print(f"      - {f.relative_to(KNOWLEDGE_DIR)}")
    else:
        print(f"\n✅ Brak duplikatów nazw plików!")
    
    # Sprawdź duplikaty treści
    print(f"\n🔍 Sprawdzanie duplikatów treści w plikach...")
    content_hashes = defaultdict(list)
    
    for file in txt_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                content_hash = hashlib.md5(content.encode()).hexdigest()
                content_hashes[content_hash].append(file)
        except Exception as e:
            print(f"   ⚠️  Błąd czytania {file.name}: {e}")
    
    duplicate_contents = {h: files for h, files in content_hashes.items() if len(files) > 1}
    
    if duplicate_contents:
        print(f"\n❌ DUPLIKATY TREŚCI ({len(duplicate_contents)} grup):")
        for idx, (hash_val, files) in enumerate(duplicate_contents.items(), 1):
            print(f"\n   Duplikat #{idx} ({len(files)} plików):")
            for file in files:
                print(f"      - {file.relative_to(KNOWLEDGE_DIR)}")
    else:
        print(f"\n✅ Brak duplikatów treści w plikach!")
    
    # Statystyki rozmiaru plików
    file_sizes = []
    for file in txt_files:
        try:
            size = file.stat().st_size
            file_sizes.append((file.name, size))
        except Exception as e:
            print(f"   ⚠️  Błąd statystyk {file.name}: {e}")
    
    if file_sizes:
        avg_size = sum(s for _, s in file_sizes) / len(file_sizes)
        print(f"\n📊 Statystyki rozmiarów plików:")
        print(f"   Średni rozmiar: {avg_size:.0f} bajtów")
        print(f"\n   Najmniejsze pliki:")
        for name, size in sorted(file_sizes, key=lambda x: x[1])[:5]:
            print(f"      {name}: {size} bajtów")
        print(f"\n   Największe pliki:")
        for name, size in sorted(file_sizes, key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {name}: {size} bajtów")


if __name__ == "__main__":
    print("\n🔍 AUDYT JAKOŚCI BAZY WIEDZY\n")
    
    # Analiza systemu plików
    analyze_filesystem()
    
    # Analiza Qdrant
    print("\n")
    analyze_qdrant_collection()
    
    print("\n" + "=" * 80)
    print("✅ ANALIZA ZAKOŃCZONA")
    print("=" * 80 + "\n")
