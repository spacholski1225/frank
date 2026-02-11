# Product Requirements Document (PRD): Frank the Assistant

**Wersja:** 1.1 (Removed External Food API)
**Status:** Ready for Development
**Platforma docelowa:** Lokalny serwer (PC → Raspberry Pi 5)
**Model danych:** Markdown-First (Obsidian Compatible)

---

## 1. Wstęp i Wizja

Frank to prywatny, lokalny asystent AI działający w modelu **"Backend-First"**.
System integruje zarządzanie życiem osobistym (zdrowie, czas, wiedza) w oparciu o lokalne pliki tekstowe.

**Kluczowa zmiana w v1.1:**
Pełna autonomia żywieniowa. Frank nie polega na zewnętrznych bazach danych żywności. Korzysta ze spersonalizowanej listy częstych posiłków użytkownika (`food_database.md`), a w przypadku nowych dań – z własnej wiedzy (LLM Estimation).

---

# 2. Architektura Techniczna

## 2.1. Tech Stack

**Core Logic:** Python 3.11+ (FastAPI)
**AI Engine:** Anthropic Client SDK

* Claude 3.5 Sonnet – logika / estymacja
* Claude Haiku – proste zadania

**Vector Store:** ChromaDB (Persistent Client) – do przeszukiwania notatek (RAG)
**Storage:** System plików (struktura folderów Markdown / Obsidian Vault)

**External Tools:**

* Google Calendar API (zarządzanie czasem)
* Notion API (opcjonalnie, jeśli nie używamy RSync)

---

## 2.2. Diagram Przepływu Danych (Żywienie)

```mermaid
graph TD
    User[Użytkownik] -->|Text: 'Zjadłem owsiankę'| Frank[Frank Agent]
    Frank -->|1. Lookup| DB[food_database.md]
    
    DB -->|Found? Yes| Log[Loguj Makro z Pliku]
    DB -->|Found? No| Estimate[Estymacja LLM]
    
    Estimate --> Log
    Log -->|Append| Daily[Daily_Logs/YYYY-MM-DD.md]
```

---

# 3. Struktura Danych i Plików

Wszystkie dane znajdują się w folderze `/data` (lub innej ścieżce synchronizowanej z Obsidianem).

## 3.1. Drzewo Katalogów

```
/frank_system
├── /configs                
│   ├── system_prompt.md    # Osobowość Franka
│   └── food_database.md    # BAZA DANYCH POSIŁKÓW (User Defined)
├── /db_chroma              # Indeks wektorowy ChromaDB
└── /obsidian_vault         # Twoje dane (User Data)
    ├── /Daily_Logs         # Dziennik
    │   └── 2024-05-20.md
    ├── /Knowledge_Base     # Notatki (Wiki)
    ├── /Inbox              # Nowe notatki od Franka
    ├── /Newsletter_Digest  
    └── shopping_list.md
```

---

## 3.2. Format `food_database.md`

Plik edytowalny przez użytkownika.
Frank parsuje go przy każdym zapytaniu o jedzenie (lub trzyma w cache).

```markdown
# Moja Baza Posiłków

| Nazwa (Alias) | Kcal | Białko (g) | Węgle (g) | Tłuszcz (g) | Jednostka |
|---------------|------|------------|-----------|-------------|-----------|
| Owsianka      | 450  | 20         | 60        | 15          | porcja    |
| Jajecznica    | 320  | 22         | 2         | 25          | 3 jajka   |
| Skyr          | 90   | 18         | 4         | 0           | kubek     |
```

---

# 4. Wymagania Funkcjonalne (Moduły)

---

## 4.1. Moduł Żywieniowy (Local Lookup & Estimate)

**Cel:** Śledzenie kalorii bez zewnętrznego API.

### Logika działania

Użytkownik wpisuje:

> "Zjadłem owsiankę i banana"

**Krok 1 (Lookup):**
Frank szuka „owsianka” i „banan” w pliku `food_database.md`.

**Krok 2 (Decyzja):**

* ✅ Znaleziono → Pobiera wartości z tabeli
* ❌ Nie znaleziono → Claude 3.5 Sonnet estymuje wartości na podstawie swojej wiedzy treningowej

**Krok 3 (Logowanie):**
Dopisuje dane do pliku dnia:
`/Daily_Logs/YYYY-MM-DD.md`

### Format logu w dzienniku

```markdown
## Dziennik Żywieniowy

| Godzina | Posiłek | Kcal | B | W | T | Źródło |
|---------|---------|------|---|---|---|--------|
| 08:30   | Owsianka| 450  | 20| 60| 15| Baza   |
| 08:30   | Banan   | 105  | 1 | 27| 0 | Estymacja |
```

---

## 4.2. Moduł Wiedzy (Obsidian RAG)

**Cel:** Wyszukiwanie informacji w Twoich notatkach.

### Indeksowanie

Proces (np. przy starcie serwera lub na żądanie `/reindex`):

* Czyta pliki `.md` z `/Knowledge_Base`
* Dzieli je na fragmenty
* Zapisuje w ChromaDB

### Query

> „Frank, jakie mam notatki o projekcie X?”

Frank wykonuje wyszukiwanie wektorowe i generuje odpowiedź.

---

## 4.3. Moduł Kalendarza (Google Calendar)

**Cel:** Zarządzanie czasem.

**Integracja:** Google Calendar API

### Funkcje:

* Sprawdzanie planu dnia („Co mam dziś?”)
* Dodawanie wydarzeń („Dodaj wizytę u dentysty”)

**Uwaga:**
Frank nie wysyła powiadomień push sam z siebie.
System polega na natywnych powiadomieniach Google Calendar w telefonie.

---

## 4.4. Newsletter & Content

**Cel:** Agregacja wiedzy.

Endpoint:

1. Przyjmuje treść
2. Frank robi podsumowanie
3. Zapisuje wynik w `/obsidian_vault/Newsletter_Digest/`

---

# 5. API Endpoints (FastAPI)

Backend komunikuje się ze światem zewnętrznym przez REST API.

| Metoda | Endpoint                | Opis                                                                 |
| ------ | ----------------------- | -------------------------------------------------------------------- |
| POST   | `/v1/chat`              | Główny endpoint konwersacyjny. Przyjmuje JSON `{"message": "tekst"}` |
| POST   | `/v1/system/refresh-db` | Przeładowuje `food_database.md` i re-indeksuje notatki w ChromaDB    |
| GET    | `/v1/status/nutrition`  | Zwraca podsumowanie kalorii z dzisiaj (JSON)                         |
| POST   | `/v1/ingest`            | Wrzuć treść (mail/artykuł) do analizy                                |

---

# 6. Roadmapa Wdrożenia (Updated)

## Faza 1: MVP (Tekst & Lokalne Jedzenie)

* [ ] Konfiguracja projektu Python (FastAPI)
* [ ] Stworzenie pliku `food_database.md` i parsera w Pythonie
* [ ] Implementacja logiki: Lookup → Fallback Estimate → Write to Markdown
* [ ] Prosty czat tekstowy w terminalu lub przez `curl`

---

## Faza 2: Pamięć (RAG & Obsidian)

* [ ] Uruchomienie ChromaDB (tryb persistent)
* [ ] Skrypt indeksujący notatki Markdown
* [ ] Podpięcie narzędzia `search_notes` pod agenta

---

## Faza 3: Czas (Google Calendar)

* [ ] Setup Google Cloud Console (Service Account)
* [ ] Implementacja narzędzi `add_event` / `get_events`

---

## Faza 4: Optymalizacja na Raspberry Pi

* [ ] Konteneryzacja (Docker)
* [ ] Testy wydajności (czas odpowiedzi Claude vs Haiku)
