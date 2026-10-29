# Apple Tag - Moduł FindMy

Ten moduł służy do pobierania pozycji urządzeń (np. AirTagów) przypisanych do Twojego konta Apple przy użyciu nieoficjalnej biblioteki `FindMy`.

## Wymagania OS (Czysty Debian)

Aby zainstalować wszystkie zależności w systemie operacyjnym Debian (lub jego pochodnych, np. Ubuntu), potrzebujesz interpretera języka Python 3 i środowiska wirtualnego, a także pakietów systemowych dla kryptografii. Wykonaj poniższe komendy:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv libffi-dev libssl-dev build-essential
```

## Instalacja

Pamiętaj o ścisłej izolacji tego modułu (znajdujesz się wewnątrz folderu `apple-tag`). Ustaw środowisko wirtualne dla zależności, aby uniknąć konfliktów.

1. Utwórz środowisko wirtualne (`venv`):
   ```bash
   python3 -m venv venv
   ```

2. Aktywuj środowisko:
   ```bash
   source venv/bin/activate
   ```

3. Zainstaluj niezbędne zależności z pliku `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *(Moduł używa biblioteki `findmy` – wewnątrz pliku `requirements.txt` zainstaluje ona również wsparcie dla paczki `anisette`, wymaganej do logowania).*

## Logowanie i przypisanie tagów

Autoryzacja wymaga użycia konta Apple ID (z uwierzytelnianiem dwuskładnikowym). Jest to jednorazowy proces interaktywny w terminalu. Zalogowanie przebiega w ten sposób:

1. Aktywuj środowisko wirtualne (jeśli nie jest włączone).
2. Uruchom skrypt konfiguracyjny z poziomu konsoli:
   ```bash
   python login_and_setup.py
   ```
3. Podaj swój adres e-mail (Apple ID) i hasło.
4. Wybierz metodę drugiego składnika autoryzacji (np. SMS, Zaufane Urządzenie) poprzez wpisanie odpowiedniego numeru z listy.
5. Przepisz kod, który przyszedł SMS-em lub wyświetlił się na urządzeniu Apple.
6. Po poprawnym logowaniu skrypt pobierze z serwerów listę Twoich urządzeń (AirTagów, iPhone'ów, MacBooków, itp.).
7. Zostaniesz poproszony o wpisanie numerów identyfikujących (oddzielonych przecinkiem, np. `0,2`), które mają być monitorowane.
8. Skrypt zapisze sesję logowania do `account.json`, pobierze odpowiednie pakiety i zapisze dane tagów do `config.json`. Wszystkie pliki stworzą się w folderze lokalnym `apple-tag`.

*Jeśli będziesz chciał zmienić śledzone urządzenia lub konto, po prostu usuń wygenerowany plik `account.json` i `config.json`, a następnie uruchom skrypt jeszcze raz.*

## Pobieranie pozycji

Aby cyklicznie pobierać pozycję tagów za pomocą konta podłączonego w poprzednim kroku:

1. Upewnij się, że poprawnie dokończony został skrypt logowania.
2. Odpal polecenie (z włączonym `venv`):
   ```bash
   python fetch_apple.py
   ```
3. Skrypt użyje lokalnej sesji do połączenia z serwerami Apple i poprosi o koordynaty urządzeń wpisanych w konfiguracji.
4. Wszystkie wyniki zapisują się formacie NDJSON (jeden obiekt JSON w każdej linijce) w globalnym folderze danych projektu – `../data/`. Nazewnictwo plików odpowiada konwencji: `YYYYMMDD-NazwaUrzadzenia.jsonl`. Oznacza to jeden plik dziennie dla poszczególnego tagu.
