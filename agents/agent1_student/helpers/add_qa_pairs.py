#!/usr/bin/env python3
"""
Script to add QA pairs (question-answer examples) to the knowledge base.
These pairs help train and improve the chatbot's responses.
"""

import json
from pathlib import Path
import uuid


QA_PAIRS = {
    "dane_osobowe": [
        {
            "question": "Jak zmienić swoje dane osobowe w systemie?",
            "answer": "Aby zmienić dane osobowe takie jak adres, imię lub nazwisko, należy złożyć odpowiednie podanie. Zmiany nr telefonu lub adresu e-mail można dokonać poprzez specjalny formularz dostępny w systemie studentów. Wszystkie zmiany wymagają potwierdzenia przez biuro.",
            "category": "dane_osobowe",
            "type": "procedure"
        },
        {
            "question": "Jakie są zasady ochrony danych osobowych dla studentów?",
            "answer": "Uniwersytet zobowiązany jest do ochrony danych osobowych studentów zgodnie z RODO. Dane przetwarzane są wyłącznie w celach związanych z realizacją studiów. Studenci mają prawo dostępu do swoich danych oraz prawo do ich poprawy.",
            "category": "dane_osobowe",
            "type": "information"
        },
        {
            "question": "Gdzie zgłosić zmianę numeru telefonu lub maila?",
            "answer": "Zmianę numeru telefonu lub adresu e-mail należy zgłosić w dekanatcie lub poprzez portal studenta. Wymagane jest wypełnienie odpowiedniego formularza. Zmiana zostaje wprowadzona w ciągu kilku dni roboczych.",
            "category": "dane_osobowe",
            "type": "procedure"
        }
    ],
    
    "egzaminy": [
        {
            "question": "Jak wygląda procedura obrony pracy dyplomowej?",
            "answer": "Obrona pracy dyplomowej odbywa się przed komisją złożoną z promotora i recenzentów. Student prezentuje pracę, a następnie odpowiada na pytania komisji. Ostateczna ocena ustalana jest przez komisję na podstawie oceny pracy i przebiegu obrony.",
            "category": "egzaminy",
            "type": "procedure"
        },
        {
            "question": "Kiedy odbywa się harmonogram obron prac dyplomowych?",
            "answer": "Harmonogram obron publikowany jest co semestr. Obiekcie dyplomowe odbywają się zazwyczaj w okresie egzaminacyjnym. Dokładne daty i godziny dostępne są w systemie i na stronie wydziału.",
            "category": "egzaminy",
            "type": "information"
        },
        {
            "question": "Jak złożyć reklamację na ocenę z egzaminu?",
            "answer": "Reklamację na ocenę egzaminu można złożyć w ciągu 5 dni od ogłoszenia wyniku. Formularz reklamacji dostępny jest w dekanatcie. Reklamacja powinna zawierać uzasadnienie i być złożona u prowadzącego zajęcia.",
            "category": "egzaminy",
            "type": "procedure"
        },
        {
            "question": "Czy mogę poprosić o przedłużenie sesji egzaminacyjnej?",
            "answer": "Tak, możliwe jest przedłużenie sesji egzaminacyjnej ze względów zdrowotnych lub innych ważnych powodów. Wniosek należy złożyć z załączonym uzasadnieniem i dokumentacją. Decyzję podejmuje dziekanat.",
            "category": "egzaminy",
            "type": "procedure"
        }
    ],
    
    "rekrutacja": [
        {
            "question": "Jakie są warunki przyjęcia na studia?",
            "answer": "Warunkami przyjęcia są: posiadanie świadectwa maturalności, spełnienie kryteriów punktowych, oraz przystąpienie do procesu rekrutacji. Szczegółowe warunki dla poszczególnych kierunków dostępne są w Regulaminie Rekrutacji.",
            "category": "rekrutacja",
            "type": "information"
        },
        {
            "question": "Czy mogę zmienić kierunek studiów?",
            "answer": "Tak, zmiana kierunku jest możliwa. Aby zmienić kierunek, należy złożyć odpowiednie podanie w dekanatcie. Zmiana wymagana przepisu do wykazania zgodności programów studiów i uwzględniania już zdobytych punktów ECTS.",
            "category": "rekrutacja",
            "type": "procedure"
        },
        {
            "question": "Jak wznowić naukę po przerwaniu studiów?",
            "answer": "Aby wznowić naukę, należy złożyć wniosek o wznowienie studiów. Wymagane jest zapoznanie się z aktualnym regulaminem studiów. Biuro weryfikuje warunki i wydaje decyzję w sprawie wznowienia.",
            "category": "rekrutacja",
            "type": "procedure"
        },
        {
            "question": "Czy mogę zrezygnować ze studiów?",
            "answer": "Tak, rezygnacja ze studiów jest możliwa. Należy złożyć odpowiednie podanie o rezygnacji w dekanatcie. Po zatwierdzeniu wniosku student otrzymuje zaświadczenie o odbyciu studiów.",
            "category": "rekrutacja",
            "type": "procedure"
        }
    ],
    
    "stypendia": [
        {
            "question": "Jakie rodzaje stypendiów są dostępne dla studentów?",
            "answer": "Dostępne są następujące rodzaje stypendiów: stypendium rektora, stypendium socjalne, stypendium dla osób niepełnosprawnych, stypendium dla sportowców, program Erasmus, oraz stypendium dla kierunku drugiego.",
            "category": "stypendia",
            "type": "information"
        },
        {
            "question": "Jak ubiegać się o stypendium?",
            "answer": "Aby ubiegać się o stypendium, należy złożyć wniosek w wyznaczonym terminie (zwykle przed sesją). Wniosek zawiera: dane osobowe, zaświadczenie o dochodach rodziny (dla stypendiów socjalnych), oraz wymagane dokumenty. Komisja rozpatruje wnioski i wydaje decyzję.",
            "category": "stypendia",
            "type": "procedure"
        },
        {
            "question": "Jaka jest wysokość stypendiów w bieżącym semestrze?",
            "answer": "Wysokość stypendiów zależy od rodzaju stypendium i sytuacji finansowej studenta. Stawki publikowane są na początku każdego semestru. Szczegółowe stawki dostępne są w informacji o funduszu stypendiów.",
            "category": "stypendia",
            "type": "information"
        },
        {
            "question": "Czy osoby niepełnosprawne mogą ubiegać się o wyższe stypendium?",
            "answer": "Tak, dla osób z niepełnosprawnościami dostępne jest pełne stypendium socjalne niezależnie od statusu materialnego. Wymagane jest przedłożenie orzeczenia o niepełnosprawności wydanego przez PKWN.",
            "category": "stypendia",
            "type": "information"
        }
    ],
    
    "urlopy_zwolnienia": [
        {
            "question": "Kiedy mogę wziąć urlop dziekański?",
            "answer": "Urlop dziekański (zwolnienie z zajęć) przyznawane jest ze względów zdrowotnych, osobistych lub zawodowych. Urlop na zwykle przyznawany na okres od kilku dni do kilku tygodni. Wniosek należy złożyć w dekanatcie.",
            "category": "urlopy_zwolnienia",
            "type": "procedure"
        },
        {
            "question": "Czy mogę być zwolniony z zajęć z wychowania fizycznego?",
            "answer": "Tak, zwolnienie z WF możliwe jest na podstawie zaświadczenia lekarskiego. Zaświadczenie powinno zawierać wskazania do zwolnienia z zajęć i okres jego ważności. Zwolnienie składa się u wyznaczonego pracownika dziekanatu.",
            "category": "urlopy_zwolnienia",
            "type": "procedure"
        }
    ]
}


def add_qa_pairs_to_knowledge_base(knowledge_dir: Path):
    """Add QA pairs to the knowledge base"""
    
    for category, qa_list in QA_PAIRS.items():
        category_dir = knowledge_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Create QA file
        qa_path = category_dir / f"{category}_qa_pairs.json"
        
        qa_data = {
            "category": category,
            "qa_pairs": [
                {
                    **qa,
                    "id": str(uuid.uuid4()),
                    "metadata": {
                        "category": category,
                        "type": qa.get("type", "general"),
                        "source": "manually_created_qa_pair"
                    }
                }
                for qa in qa_list
            ]
        }
        
        with open(qa_path, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, ensure_ascii=False, indent=2)
        
        print(f"Created QA pairs for {category}: {qa_path} ({len(qa_list)} QA pairs)")
        
        # Also add QA pairs to the main documents file
        docs_path = category_dir / f"{category}_documents.json"
        if docs_path.exists():
            with open(docs_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Add QA pairs as special documents
            for qa in qa_list:
                qa_doc = {
                    "id": str(uuid.uuid4()),
                    "category": category,
                    "source_file": f"{category}_qa_pairs",
                    "content": f"Pytanie: {qa['question']}\n\nOdpowiedź: {qa['answer']}",
                    "metadata": {
                        "category": category,
                        "source": "qa_pair",
                        "question": qa["question"],
                        "answer": qa["answer"],
                        "type": qa.get("type", "general")
                    }
                }
                documents.append(qa_doc)
            
            with open(docs_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            
            print(f"  Added {len(qa_list)} QA pairs to {category}_documents.json")


def main():
    # Dynamiczna ścieżka bazująca na lokalizacji pliku
    base_dir = Path(__file__).parent.parent
    knowledge_dir = base_dir / "knowledge"
    
    print("Adding QA pairs to knowledge base...\n")
    add_qa_pairs_to_knowledge_base(knowledge_dir)
    
    # Update all_documents.json
    all_docs_path = knowledge_dir / "all_documents.json"
    with open(all_docs_path, 'r', encoding='utf-8') as f:
        all_documents = json.load(f)
    
    for category, qa_list in QA_PAIRS.items():
        for qa in qa_list:
            qa_doc = {
                "id": str(uuid.uuid4()),
                "category": category,
                "source_file": f"{category}_qa_pairs",
                "content": f"Pytanie: {qa['question']}\n\nOdpowiedź: {qa['answer']}",
                "metadata": {
                    "category": category,
                    "source": "qa_pair",
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "type": qa.get("type", "general")
                }
            }
            all_documents.append(qa_doc)
    
    with open(all_docs_path, 'w', encoding='utf-8') as f:
        json.dump(all_documents, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal documents in all_documents.json: {len(all_documents)}")
    print("\nQA pairs addition complete!")


if __name__ == "__main__":
    main()
