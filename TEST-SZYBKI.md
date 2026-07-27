# Test na zywo — bez budowania instalatora

## Najszybciej: uruchom.bat

1. Rozpakuj paczke
2. Kliknij dwa razy **`uruchom.bat`**
3. Okno otwiera sie od razu, PIN **1234**

Plik sam sprawdzi, czy jest Python i czy jest biblioteka Pillow —
jesli brakuje Pillow, doinstaluje ja jednorazowo.

Poprawiasz, zamykasz okno, klikasz `uruchom.bat` ponownie. Zadnego czekania.

## Jednorazowa instalacja Pythona

Jesli `uruchom.bat` napisze, ze nie znalazl Pythona:

1. **python.org/downloads**
2. Zolty przycisk **Download Python**
3. **Na pierwszym ekranie instalatora, na dole, zaznacz
   „Add python.exe to PATH"** — to najwazniejsze
4. **Install Now** -> **Close**

Potem `uruchom.bat` juz zadziala.

## Co sprawdzic w tej wersji

- **Podglad** — czy zdjecie wypelnia cale okno i czy panel po prawej
  nie zaslania zadnego slupka
- **Kliknij SYMULUJ PRZEJAZD** — czy panele znikaja na czas ruchu
  i wracaja po zakonczeniu
- **Zmien rozmiar okna** — czy kadr sam sie dopasowuje
- **Ustawienia obiektu** (MODULY -> Edytuj) — trzy tryby paneli:
  chowaj podczas ruchu / zawsze widoczne / zawsze schowane
- **Tryb jasny** w prawym gornym rogu
- **STEROWNIK** — Polacz, kod dostepu, tryb pracy, kopia danych
- **HISTORIA I RAPORTY** — czy przejazd sie zapisal, czy raport sie otwiera

## Kiedy budowac instalator

Dopiero gdy wersja ma isc na komputer dyzurki albo do pokazania komus.
Do samego klikania i ogladania wystarczy `uruchom.bat`.

## Gdzie leza dane

`%APPDATA%\ZAPORA-AWF` — wklej w pasek adresu Eksploratora.

Chcesz zaczac od czystej bazy: skasuj stamtad `baza.json` i uruchom ponownie.
Program utworzy nowa z przykladowymi numerami, PIN wroci do 1234.
