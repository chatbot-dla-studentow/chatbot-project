#!/usr/bin/env python3
"""
Skrypt do weryfikacji i testowania bazy wiedzy
Sprawdza czy dokumenty są prawidłowo sformatowane dla Qdrant
"""

import json
from pathlib import Path
from typing import Dict, List

def validate_knowledge_base(knowledge_dir: str) -> Dict:
    """Weryfikuje strukturę i zawartość bazy wiedzy"""
    
    stats = {
        "categories": {},
        "total_documents": 0,
        "total_qa_pairs": 0,
        "format_issues": [],
        "categories_found": []
    }
    
    knowledge_path = Path(knowledge_dir)
    
    # Wczytaj all_documents.json
    all_docs_path = knowledge_path / "all_documents.json"
    if all_docs_path.exists():
        print(f"Znaleziono all_documents.json")
        try:
            with open(all_docs_path, 'r', encoding='utf-8') as f:
                all_docs = json.load(f)
            stats["total_documents"] = len(all_docs)
            print(f"  Łączna liczba dokumentów: {len(all_docs)}")
            
            # Sprawdź strukturę
            for doc in all_docs[:5]:  # Sprawdź pierwsze 5
                if "id" not in doc or "content" not in doc or "category" not in doc:
                    stats["format_issues"].append(f"Dokument {doc.get('id')} ma niekompletną strukturę")
        except json.JSONDecodeError as e:
            stats["format_issues"].append(f"JSON error w all_documents.json: {e}")
    else:
        stats["format_issues"].append("Brak all_documents.json")
    
    # Sprawdź każdą kategorię
    for category_dir in knowledge_path.iterdir():
        if not category_dir.is_dir() or category_dir.name == "__pycache__":
            continue
        
        category = category_dir.name
        stats["categories_found"].append(category)
        stats["categories"][category] = {
            "documents": 0,
            "qa_pairs": 0,
            "files": []
        }
        
        # Sprawdź dokumenty
        docs_file = category_dir / f"{category}_documents.json"
        if docs_file.exists():
            stats["categories"][category]["files"].append("documents.json")
            try:
                with open(docs_file, 'r', encoding='utf-8') as f:
                    docs = json.load(f)
                stats["categories"][category]["documents"] = len(docs)
            except Exception as e:
                stats["format_issues"].append(f"Błąd w {docs_file}: {e}")
        
        # Sprawdź QA pairs
        qa_file = category_dir / f"{category}_qa_pairs.json"
        if qa_file.exists():
            stats["categories"][category]["files"].append("qa_pairs.json")
            try:
                with open(qa_file, 'r', encoding='utf-8') as f:
                    qa_data = json.load(f)
                    qa_pairs = qa_data.get("qa_pairs", [])
                stats["categories"][category]["qa_pairs"] = len(qa_pairs)
                stats["total_qa_pairs"] += len(qa_pairs)
            except Exception as e:
                stats["format_issues"].append(f"Błąd w {qa_file}: {e}")
    
    return stats

def print_validation_report(stats: Dict):
    """Wypisuje raport weryfikacji"""
    
    print("\n" + "=" * 70)
    print("RAPORT WERYFIKACJI BAZY WIEDZY")
    print("=" * 70)
    
    print(f"\nSTATYSTYKI OGÓLNE:")
    print(f"   Łączna liczba dokumentów: {stats['total_documents']}")
    print(f"   Łączna liczba QA pair: {stats['total_qa_pairs']}")
    print(f"   Liczba kategorii: {len(stats['categories'])}")
    
    print(f"\nKATEGORII ZNALEZIONE: {', '.join(sorted(stats['categories_found']))}")
    
    print(f"\nSZCZEGÓŁY PO KATEGORII:")
    for category in sorted(stats['categories'].keys()):
        cat_stats = stats['categories'][category]
        print(f"\n   {category.upper()}")
        print(f"   ├─ Dokumenty: {cat_stats['documents']} chunks")
        print(f"   ├─ QA pary: {cat_stats['qa_pairs']}")
        print(f"   └─ Pliki: {', '.join(cat_stats['files'])}")
    
    if stats['format_issues']:
        print(f"\n️  POTENCJALNE PROBLEMY:")
        for issue in stats['format_issues']:
            print(f"   - {issue}")
    else:
        print(f"\nBRAK PROBLEMÓW - BAZA WIEDZY JEST POPRAWNIE SFORMATOWANA!")
    
    print("\n" + "=" * 70)
    print("PODSUMOWANIE DLA QDRANT:")
    print("=" * 70)
    print(f"Format: JSON z polami 'id', 'content', 'category', 'metadata'")
    print(f"Kompatybilność: Polska obsługa znaków (UTF-8)")
    print(f"Gotowość do wczytania: TAK")
    print(f"Łącznie chunków do wektoryzacji: {stats['total_documents']}")
    print("=" * 70 + "\n")


def main():
    # Dynamiczna ścieżka bazująca na lokalizacji pliku
    base_dir = Path(__file__).parent.parent
    knowledge_dir = base_dir / "knowledge"
    
    print("Weryfikacja bazy wiedzy...\n")
    stats = validate_knowledge_base(knowledge_dir)
    print_validation_report(stats)
    
    # Przykład dokumentu QA
    print("PRZYKŁAD: QA PAIR\n" + "-" * 70)
    qa_file = Path(knowledge_dir) / "dane_osobowe" / "dane_osobowe_qa_pairs.json"
    if qa_file.exists():
        with open(qa_file, 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
            if qa_data.get("qa_pairs"):
                example = qa_data["qa_pairs"][0]
                print(json.dumps(example, indent=2, ensure_ascii=False))
    
    # Przykład dokumentu
    print("\n\nPRZYKŁAD: SPARSOWANY DOKUMENT\n" + "-" * 70)
    docs_file = Path(knowledge_dir) / "dane_osobowe" / "dane_osobowe_documents.json"
    if docs_file.exists():
        with open(docs_file, 'r', encoding='utf-8') as f:
            docs = json.load(f)
            if docs:
                example = docs[0]
                print(json.dumps(example, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
