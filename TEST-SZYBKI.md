# Jak testowac bez czekania na GitHuba

Budowanie instalatora trwa 3-5 minut. Przy kazdej drobnej poprawce to za dlugo.
Ponizej sposob, zeby zobaczyc zmiany **od razu**.

## Jednorazowa instalacja Pythona (5 minut, raz na zawsze)

1. Wejdz na **python.org/downloads**
2. Zolty przycisk **Download Python**
3. Uruchom instalator i **na pierwszym ekranie, na dole, zaznacz
   „Add python.exe to PATH"** — to jest najwazniejsze
4. **Install Now** -> **Close**

## Test aplikacji — 2 sekundy

Klikasz dwa razy na plik **`zapora_awf.py`** w rozpakowanym folderze.
Okno otwiera sie natychmiast. Zamykasz, poprawiasz, otwierasz ponownie.

Zadnego budowania, zadnego czekania.

Jesli plik otwiera sie w Notatniku zamiast sie uruchomic:
prawy klik -> **Otworz za pomoca** -> **Python**.

## Kiedy budowac instalator

Dopiero gdy wersja jest gotowa do zainstalowania na komputerze dyzurki
albo do pokazania komus. Do samego sprawdzania wygladu i klikania —
uruchamiaj plik .py bezposrednio.

## Co testowac po kazdej zmianie

- **Podglad** — kliknij SYMULUJ PRZEJAZD, obejrzyj pelny cykl
- **Tryb jasny/ciemny** — przelacz i sprawdz czy wszystko czytelne
- **Numery** — dodaj kogos z harmonogramem pn-pt 06:00-18:00 i sprawdz
  kolumne STAN
- **Historia** — czy przejazd sie zapisal, czy raport sie generuje
- **O programie** — czy wersja sie zgadza

## Gdzie leza dane podczas testow

`%APPDATA%\ZAPORA-AWF` — wklej w pasek adresu Eksploratora.

Chcesz zaczac od czystej bazy: skasuj stamtad `baza.json` i uruchom program
ponownie. Utworzy nowa z przykladowymi numerami, PIN wroci do 1234.
