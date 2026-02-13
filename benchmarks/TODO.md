# TODO - System Benchmarkingu LLM
Lista planowanych usprawnień i funkcji do dodania w module benchmarków.

## Zrealizowane
- [x] **System Warm-up:** Implementacja ładowania modeli do GPU przed właściwym testem.
- [x] **Hardware Logging:** Automatyczne wykrywanie i logowanie specyfikacji sprzętowej (CPU, RAM, GPU) w raportach.
- [x] **Wizualizacja Latency:** Generowanie wykresów porównawczych przy użyciu Matplotlib.
- [x] **Wersjonowanie Raportów:** System zapisu raportów z sygnaturą czasową w dedykowanym folderze.
- [x] **Zwiększenie Limitów Generowania:** Podniesienie `num_predict` i `num_ctx` dla uzyskania pełnych odpowiedzi merytorycznych.
- [x] **Context Caching:** Mechanizm zapewniający identyczny wsad danych dla każdego testowanego modelu.

## Jakość i Metryki (W toku)
- [ ] **Stabilizacja LLM-as-a-Judge:** Naprawa parsera JSON i optymalizacja promptu sędziego (Llama3) dla rzetelniejszych ocen automatycznych.
- [ ] **Zbiór Ground Truth:** Przygotowanie bazy "złotych odpowiedzi" (10-20 przypadków) dla metryk podobieństwa semantycznego.
- [ ] **Optymalizacja Systemu Promptu:** Testy różnych wersji promptu systemowego w celu eliminacji odpowiedzi w języku angielskim.

## Rozszerzenie Monitoringu
- [ ] **Zużycie VRAM:** Dodanie automatycznego logowania szczytowego użycia pamięci GPU dla każdego modelu.
- [ ] **Tokeny na sekundę (TPS):** Dodanie metryki szybkości generowania tekstu (throughput).
- [ ] **Weryfikacja RAG:** Analiza wpływu parametru `top_k` i `score_threshold` na jakość odpowiedzi.

## Funkcjonalność
- [ ] **Eksport do CSV/JSON:** Dodanie opcji eksportu wyników do formatów ułatwiających dalszą analizę w Excelu/Pandas.
- [ ] **Testy Cross-referential:** Dodanie pytań wymagających syntezy wiedzy z kilku różnych dokumentów/kategorii.

## Organizacja
- [ ] **Auto-cleanup:** Skrypt do czyszczenia starych raportów i wykresów (np. starszych niż 30 dni).
- [ ] **Interaktywny Dashboard:** Prosty widok w Streamlit do przeglądania historycznych wyników benchmarków.

## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Mikołaj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Paweł Ponikowski (pponikowski)
