#!/usr/bin/env python3
"""
Knowledge Manager - Interfejs CLI do zarządzania bazą wiedzy Agent1
Centralne narzędzie do operacji na bazie wiedzy w Qdrant
"""
import sys
import os
from pathlib import Path

# Dodaj helpers do path
sys.path.insert(0, str(Path(__file__).parent / "helpers"))

def print_menu():
    """Wyświetla menu główne"""
    print("\n" + "=" * 70)
    print("KNOWLEDGE MANAGER - Agent1 Student")
    print("=" * 70)
    print("\nZARZĄDZANIE BAZĄ WIEDZY:")
    print("  1. Parse  - Parsuj pliki źródłowe (txt, docx, pdf) → JSON")
    print("  2. Load   - Załaduj dokumenty JSON do Qdrant + embeddingi (pełne)")
    print("  3. Update - Aktualizuj bazę (dodaj tylko nowe dokumenty)")
    print("  4. Verify - Weryfikuj strukturę i zawartość bazy wiedzy")
    print("  5. Check  - Sprawdź jakość danych w Qdrant (duplikaty)")
    print("  6. Add QA - Dodaj pary pytanie-odpowiedź")
    print("\nZARZĄDZANIE KOLEKCJAMI:")
    print("  7. Init Logs - Inicjalizuj kolekcje logów (query_logs, qa_logs)")
    print("  8. Delete - Usuń kolekcję z Qdrant")
    print("\nINFORMACJE:")
    print("  9. Status - Pokaż status wszystkich kolekcji")
    print("  h. Help - Pokaż szczegółową pomoc")
    print("  0. Exit - Wyjdź")
    print("\n" + "=" * 70)

def run_script(script_name: str):
    """Uruchamia wybrany skrypt z folderu helpers"""
    helpers_dir = Path(__file__).parent / "helpers"
    script_path = helpers_dir / script_name
    
    if not script_path.exists():
        print(f"Błąd: Skrypt {script_name} nie istnieje!")
        return
    
    print(f"\n▶️  Uruchamiam: {script_name}")
    print("-" * 70)
    
    # Uruchom skrypt w tym samym procesie
    import subprocess
    result = subprocess.run([sys.executable, str(script_path)], cwd=str(helpers_dir.parent))
    
    print("-" * 70)
    if result.returncode == 0:
        print(f"{script_name} zakończony sukcesem")
    else:
        print(f"{script_name} zakończony z błędem (kod: {result.returncode})")

def show_status():
    """Wyświetla status kolekcji w Qdrant"""
    print("\nSTATUS KOLEKCJI QDRANT")
    print("=" * 70)
    
    try:
        from qdrant_client import QdrantClient
        
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        
        print(f"Łączenie z Qdrant ({qdrant_host}:{qdrant_port})...")
        client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        collections = client.get_collections().collections
        
        if not collections:
            print("\n️  Brak kolekcji w Qdrant")
            return
        
        print(f"\nZnaleziono {len(collections)} kolekcji:\n")
        
        for collection in collections:
            info = client.get_collection(collection.name)
            print(f"  • {collection.name}")
            print(f"    ├─ Punkty: {info.points_count}")
            print(f"    ├─ Status: {info.status}")
            print(f"    └─ Rozmiar wektora: {info.config.params.vectors.size}")
            print()
        
    except Exception as e:
        print(f"\nBłąd: {e}")
        print("Upewnij się, że Qdrant jest uruchomiony i dostępny.")

def show_help():
    """Wyświetla szczegółową pomoc"""
    print("\n" + "=" * 70)
    print("SZCZEGÓŁOWA POMOC")
    print("=" * 70)
    
    help_text = """
WORKFLOW ZARZĄDZANIA BAZĄ WIEDZY:

1️⃣  PARSE (parse_knowledge_base.py)
   ├─ Parsuje pliki źródłowe z chatbot-baza-wiedzy-nowa/
   ├─ Wspiera: .txt, .docx, .doc, .pdf
   ├─ Tworzy strukturę JSON w folderze knowledge/
   └─ Kategoryzuje dokumenty automatycznie

2️⃣  LOAD (load_knowledge_base.py)
   ├─ Wczytuje dokumenty JSON z knowledge/
   ├─ Generuje embeddingi używając Ollama (nomic-embed-text)
   ├─ Ładuje do kolekcji 'agent1_student' w Qdrant
   ├─ UWAGA: Usuwa istniejącą kolekcję i tworzy nową (pełny reload)
   └─ Automatycznie pull model jeśli brak

3️⃣  UPDATE (update_knowledge.py)
   ├─ Inkrementalna aktualizacja bazy wiedzy
   ├─ Porównuje istniejące dokumenty z nowymi (hash MD5)
   ├─ Dodaje TYLKO nowe dokumenty bez usuwania starych
   ├─ Szybsze i bezpieczniejsze niż pełny LOAD
   └─ Idealne do regularnych aktualizacji

4️⃣  VERIFY (verify_knowledge_base.py)
   ├─ Weryfikuje strukturę plików JSON
   ├─ Sprawdza kompletność kategorii
   ├─ Wyświetla statystyki dokumentów i QA pairs
   └─ Wykrywa błędy formatowania

5️⃣  CHECK (check_knowledge_quality.py)
   ├─ Analizuje dane w Qdrant
   ├─ Wykrywa duplikaty (content hash)
   ├─ Sprawdza kategoryzację
   └─ Generuje raport jakości

6️⃣  ADD QA (add_qa_pairs.py)
   ├─ Dodaje przykładowe pary pytanie-odpowiedź
   ├─ Wzbogaca bazę wiedzy o kontekst
   └─ Poprawia jakość odpowiedzi chatbota

7️⃣  INIT LOGS (init_log_collections.py)
   ├─ Tworzy kolekcje: agent1_query_logs, agent1_qa_logs
   ├─ Używane do logowania zapytań użytkowników
   └─ Wymaga działającego Ollama (embeddingi)

8️⃣  DELETE (delete_qdrant_collection.py)
   ├─ Usuwa kolekcję z Qdrant
   ├─ UWAGA: Operacja nieodwracalna!
   └─ Przydatne przy ponownym ładowaniu danych

ZMIENNE ŚRODOWISKOWE:
   QDRANT_HOST      - Host Qdrant (default: localhost)
   QDRANT_PORT      - Port Qdrant (default: 6333)
   OLLAMA_URL       - URL Ollama API (default: http://localhost:11434)

STRUKTURA KATALOGÓW:
   chatbot-baza-wiedzy-nowa/  - Pliki źródłowe (txt, docx, pdf)
   knowledge/                 - Sparsowane dokumenty JSON
   helpers/                   - Skrypty zarządzania

PRZYKŁADOWY WORKFLOW:
   
   PIERWSZA INSTALACJA:
   1. Dodaj pliki do chatbot-baza-wiedzy-nowa/
   2. Uruchom PARSE aby sparsować do JSON
   3. Uruchom VERIFY aby sprawdzić strukturę
   4. Uruchom LOAD aby załadować do Qdrant (pełny import)
   5. Uruchom CHECK aby zweryfikować jakość
   6. (Opcjonalnie) ADD QA aby dodać przykłady
   
   REGULARNA AKTUALIZACJA:
   1. Dodaj nowe pliki do chatbot-baza-wiedzy-nowa/
   2. Uruchom PARSE aby sparsować nowe dokumenty
   3. Uruchom UPDATE aby dodać tylko nowe (szybsze!)
   4. Uruchom CHECK aby sprawdzić kompletność
   
   RÓŻNICA LOAD vs UPDATE:
      • LOAD  - Usuwa całą kolekcję i tworzy nową (wolniejszy)
      • UPDATE - Dodaje tylko nowe dokumenty (szybszy, bezpieczniejszy)
    """
    print(help_text)
    print("=" * 70)

def main():
    """Główna pętla programu"""
    
    while True:
        print_menu()
        
        try:
            choice = input("\nWybierz opcję (0-9, h): ").strip().lower()
            
            if choice == "0":
                print("\nDo widzenia!")
                break
            
            elif choice == "1":
                run_script("parse_knowledge_base.py")
            
            elif choice == "2":
                run_script("load_knowledge_base.py")
            
            elif choice == "3":
                run_script("update_knowledge.py")
            
            elif choice == "4":
                run_script("verify_knowledge_base.py")
            
            elif choice == "5":
                run_script("check_knowledge_quality.py")
            
            elif choice == "6":
                run_script("add_qa_pairs.py")
            
            elif choice == "7":
                run_script("init_log_collections.py")
            
            elif choice == "8":
                print("\n️  UWAGA: Ta operacja jest nieodwracalna!")
                confirm = input("Czy na pewno chcesz usunąć kolekcję? (tak/nie): ").strip().lower()
                if confirm == "tak":
                    run_script("delete_qdrant_collection.py")
                else:
                    print("Operacja anulowana")
            
            elif choice == "9":
                show_status()
            
            elif choice == "h":
                show_help()
            
            else:
                print("Nieprawidłowa opcja. Wybierz 0-9 lub h.")
            
            input("\n⏎ Naciśnij Enter aby kontynuować...")
            
        except KeyboardInterrupt:
            print("\n\nPrzerwano przez użytkownika")
            break
        except Exception as e:
            print(f"\nBłąd: {e}")
            input("\n⏎ Naciśnij Enter aby kontynuować...")

if __name__ == "__main__":
    print("\nKnowledge Manager dla Agent1 Student")
    print("Katalog roboczy:", Path(__file__).parent)
    
    # Sprawdź czy folder helpers istnieje
    helpers_dir = Path(__file__).parent / "helpers"
    if not helpers_dir.exists():
        print(f"\nBłąd: Folder helpers nie istnieje!")
        print(f"   Oczekiwana ścieżka: {helpers_dir}")
        sys.exit(1)
    
    main()
