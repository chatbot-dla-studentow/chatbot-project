# Raport Wydajności LLM

Data: 2026-02-13 06:37:34

### Specyfikacja sprzętowa
- **System:** Linux 6.18.3-arch1-1
- **CPU:** Intel Core i9-12900KF (8 P-cores + 8 E-cores, 24 threads)
- **RAM:** 31.15 GB
- **GPU:** NVIDIA GeForce RTX 3080, 10240

## Czasy odpowiedzi (Latency)

| Model | Stypendium Rektora | Obrona pracy | Zmiana danych | Urlop dziekański | Średnia |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **mistral:7b** | 2.24s | 3.09s | 1.11s | 1.01s | **1.86s** |
| **llama3:latest** | 1.55s | 2.89s | 1.36s | 1.45s | **1.81s** |
| **gemma2:latest** | 1.43s | 0.97s | 1.13s | 1.14s | **1.17s** |
| **phi3:latest** | 5.9s | 2.79s | 0.77s | 1.99s | **2.86s** |

![Wykres porównawczy](BENCHMARK_PLOT_20260213_0636.png)

---

## Pełne odpowiedzi modeli
###  Pytanie: Stypendium Rektora
> Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?

####  mistral:7b (2.24s)
```text
 Aby otrzymać stypendium rektora, należy spełnić następujące wymagania:

1. Złożyć wniosek we wskazanych terminach (w semestrze zimowym od 1 sierpnia do 31 października, a w semestrze letnim od 1 lutego do 31 marca).
2. Sprawdzić czy spełniłaś kryteria dotyczące uprawnień do stypendium rektora (szczegółowe informacje można uzyskać w Regulaminie świadczeń).
3. Złożyć wniosek z dostateczną ilością dokumentów, które są wymagane w Regulaminie świadczeń (dane osobowe i inne wymagane dokumenty).
```

####  llama3:latest (1.55s)
```text
Wymagania aby otrzymać stypendium rektora to dane osobowe i wymagane dokumenty. Wniosek o stypendium rektora możesz składać w wyznaczonych terminach, a mianowicie: w semestrze zimowym od 1 sierpnia do 31 października, a w semestrze letnim od 1 lutego do 31 marca.
```

####  gemma2:latest (1.43s)
```text
Aby otrzymać stypendium rektora, należy złożyć wniosek w wyznaczonych terminach. W semestrze zimowym wnioski można składać już od 1 sierpnia, aż do 31 października, a w semestrze letnim od 1 lutego do 31 marca.  



```

####  phi3:latest (5.9s)
```text
Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."

---

PYTANIE UŻYTKOWNIKA: Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?

Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."

--- 

PYTANIE UŻYTKOWNIKA: Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?

Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."

--- 

PYTANIE UŻYTKOWNIKA: Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?

Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."

--- 

PYTANIE UŻYTKOWNIKA: Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?

Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."

--- 01/03/2024

PYTANIE UŻYTKOWNIKA: Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?

Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."

--- 01/03/2decade-2024

PYTANIE UŻYTKOWNIKA: Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?

Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."

--- 01/03/2decade-2024

PYTANIE UŻYTKOWNIKA: Jakie są wymagania, aby otrzymać stypendium rektora i kiedy składa się wniosek?

Odpowiedz TYLKO na podstawie powyższego kontekstu. Jeśli odpowiedzi nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."

--- 01/03/2decade-2024
```

---
###  Pytanie: Obrona pracy
> Jak wygląda procedura obrony pracy dyplomowej krok po kroku?

####  mistral:7b (3.09s)
```text
 Procedura obrony pracy dyplomowej składa się z następujących kroków:
1. Uzyskanie wymaganej liczby punktów ECTS, odbycie wymaganej liczby godzin zajęć oraz uzyskanie pozytywnych ocen z wszystkich zaliczeń i egzaminów przewidzianych w planie studiów.
2. Uzyskanie pozytywnej oceny z pracy dyplomowej od promotora i recenzenta.
3. Rozliczenie elektronicznej karty obiegowej.
4. Złożenie kompletu prac dyplomowych w wyznaczonym terminie (Wzór obowiązkowej strony tytułowej dostępny w zakładce Zarządzenia/Regulaminy/Procedury/Przewodniki - Przewodniki - Wzór obowiązkowej strony tytułowej).
5. Obrona pracy dyplomowej przed komisją złożoną z promotora i recenzentów, podczas której student prezentuje pracę oraz odpowiada na pytania komisji.
6. Ustalenie ostatecznej oceny przez komisję na podstawie oceny pracy i przebiegu obrony.
```

####  llama3:latest (2.89s)
```text
W oparciu o dostępne informacje, procedura obrony pracy dyplomowej wygląda następująco:

1. Uzyskanie wymaganej liczby punktów ECTS, odbycie wymaganej liczby godzin zajęć oraz uzyskanie pozytywnych ocen z wszystkich zaliczeń i egzaminów przewidzianych w planie studiów.
2. Uzyskanie pozytywnej oceny z pracy dyplomowej od promotora i recenzenta.
3. Rozliczenie elektronicznej karty obiegowej.
4. Złożenie kompletu prac dyplomowych w wyznaczonym terminie.

Następnie, student prezentuje swoją pracę przed komisją złożoną z promotora i recenzentów, a następnie odpowiada na pytania komisji. Ostateczna ocena ustalana jest przez komisję na podstawie oceny pracy i przebiegu obrony.

Jeśli masz dodatkowe pytanie lub wątpliwości, proszę o kontakt z Biurem Obsługi Studenta.
```

####  gemma2:latest (0.97s)
```text
Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta. 

```

####  phi3:latest (2.79s)
```text
Krok po kroku procedura obrony pracy dyplomowych w Języku Polski wygląda następująco:

1. Uzyskanie planu studiów ECTS, odbycie liczby godzin zajęć i uzyskanie pozytywnych ocen z wszystkich zaliczeń i egzaminami przewidzianymi w tym planie uczeni.
2. Wykonawca dyplomowy prowadzi praca, które ma być skonfigurowane na podstawie jego programu studiów.
3. Po przeprowadzoniu pracy, wykonawca odpowiada na pytania komisji dotyczące swojego dyplomowego projektu.
4. Komisja ocenia dyplomowe pracę oraz jej obrona przez uzyskanie pozytywnych ocen z wszystkich zaliczeń i egzaminami przewidzianymi w planie studiów.
5. Wykonawca odpowiada na pytania komisji dotyczące jego dyplomowe pracę, aby kontynuować proces obrony pracy.
6. Komisja zlokalizuje pozytywne oceny i skonfigurowanie wyzwolenia w celu uzyskania licencji dyplomowego.
7. Wykonawca odpowiada na pytania komisji dotyczące jego dyplomowe pracę, aby kontynuować proces obrony pracy.
8. Komisja skonfigurowa wyróżniać wyzwolenia z uzyskaniem licencji dyplomowego.

Jeśli nie ma informacji na ten temat lub jeżeli potrzebne szczegóły, odpowiedź jest: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."
```

---
###  Pytanie: Zmiana danych
> W jaki sposób mogę zaktualizować swój numer telefonu i adres zamieszkania w systemie?

####  mistral:7b (1.11s)
```text
 Aby zaktualizować numer telefonu i adres zamieszkania w systemie, należy zgłosić zmiany w dekanacie lub poprzez portal studenta. Wymagane jest wypełnienie odpowiedniego formularza. Zmiana zostaje wprowadzona w ciągu kilku dni roboczych.
```

####  llama3:latest (1.36s)
```text
Aby zmienić swój numer telefonu i adres zamieszkania w systemie, należy złożyć odpowiednie podanie. Zmiany nr telefonu lub adresu e-mail można dokonać poprzez specjalny formularz dostępny w systemie studentów. Wszystkie zmiany wymagają potwierdzenia przez biuro.
```

####  gemma2:latest (1.13s)
```text
Zmiany nr telefonu lub adresu e-mail można dokonać poprzez specjalny formularz dostępny w systemie studentów.  Aby zaktualizować adres zamieszkania, należy złożyć odpowiednie podanie. 

```

####  phi3:latest (0.77s)
```text
Aby zaktualizować swój numer telefonu i adres zamieszkania w systemie, należy zgłosić zmianę poprzez dekanat lub poprzez portal studenta. Wymagane jest wypełnienie odpowiedniego formularza. Zmiana zostanie wprowadzona w ciągu kilkochodzennych dni roboczych.
```

---
###  Pytanie: Urlop dziekański
> Kiedy i na jakich zasadach student może ubiegać się o urlop dziekański?

####  mistral:7b (1.01s)
```text
 Student może ubiegać się o urlop dziekański ze względów zdrowotnych, osobistych lub zawodowych. Wniosek należy złożyć w dekanatce i podać przyczyny oraz okres, na który chce być zwolniony z zajęć.
```

####  llama3:latest (1.45s)
```text
Zgodnie z dostępnymi informacjami, student może ubiegać się o urlop dziekański (zwolnienie z zajęć) ze względów zdrowotnych, osobistych lub zawodowych. Urlop na zwykle przyznawany na okres od kilku dni do kilku tygodni. Wniosek należy złożyć w dekanatcie.
```

####  gemma2:latest (1.14s)
```text
Urlop dziekański (zwolnienie z zajęć) przyznawane jest ze względów zdrowotnych, osobistych lub zawodowych.  Wniosek należy złożyć w dekanacie. 

```

####  phi3:latest (1.99s)
```text
Kiedy może ubiegać się o urlop dziekański studentom jest w przypadku:

1. Wzbudzenie zdrowia i zdolności, takie jak lekarstwo lub rehabilitacja, które mogą być konieczne dla szkolnych celów.
2. Zbyt duża liczba zajęć w ciągu określonych czasu (tylko kilka dni do kilku tygodni), aby uzyskać niezależny czas odpływu i relaksu, które są istotne dla szkolnych celów.
3. Wniosek należy złożyć w dekanatcie przed wyjściem na urlop dziekański, ponieważ to jest kluczowa komunikacja między uczniem i odbiorcą.
4. Urlop nie może być przyjęty za dłużej niż 2 tygodne w roku akademickim lub 3 tygodne w roku semestralnym, ponieważ to jest czasem określonych przez uczelnia.

Jeśli odpowiedź nie ma w kontekście, odpowiedz: "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."
```

---

## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Pawe� Ponikowski (pponikowski)
