# ZAPORA-AWF v4.4

Akademia Wychowania Fizycznego Jozefa Pilsudskiego w Warszawie — Straz Akademicka.
System kontroli wjazdu: zapora slupkowa ze slupkami chowanymi w jezdnie.

Wersja demonstracyjna — animacja i pelna konfiguracja dzialaja,
moduly GSM nie sa jeszcze podpiete.

## NOWE w v4.4 — pelne przebrandowanie na AWF

Usuniete zostaly wszystkie oznaczenia firmy zewnetrznej:

| gdzie | bylo | jest |
|---|---|---|
| Wydawca w oknie „O programie" | Monter24h.pl | AWF Warszawa |
| Metryczka pliku .exe | Monter24h.pl | AWF Warszawa |
| Prawa autorskie | Monter24h.pl | AWF Warszawa |
| Instalator — producent | Monter24h.pl | Akademia Wychowania Fizycznego w Warszawie |
| Instalator — strona | monter24h.pl | awf.edu.pl |
| Naglowek raportu | Monter24h.pl | nazwa jednostki z ustawien |
| Stopka raportu | Monter24h.pl | Akademia Wychowania Fizycznego w Warszawie |
| Logo na szafce (wariant szlabanu) | M24h | AWF |
| Identyfikator w manifescie | Monter24h.ZaporaAWF | AWF.ZaporaAWF |

**Wazne — PIN dziala dalej.** Zmienil sie sposob szyfrowania kodu PIN
(usunieta stara nazwa firmy z klucza). Program przy logowaniu uznaje rowniez
skrot z poprzedniej wersji i przy pierwszym poprawnym wejsciu **sam przepisuje
go na nowy format**. Nie musisz nic robic, PIN zostaje ten sam.

Jedyne dwa miejsca, gdzie stara nazwa wciaz wystepuje w kodzie, sa techniczne
i niewidoczne dla uzytkownika: sciezka starego katalogu danych oraz stary klucz
PIN — oba sluza wylacznie przeniesieniu Twoich danych. Po pierwszym uruchomieniu
mozna je usunac; powiedz, kiedy chcesz to zrobic.

Nazwe jednostki widoczna w naglowku okna i w raportach zmieniasz w pliku
`baza.json` (katalog `%APPDATA%\ZAPORA-AWF`), sekcja `marka`.

## NOWE w v4.3 — slupki odwzorowane z rzeczywistych

Wyglad slupkow poprawiony wedlug zdjec realnych bollardow przemyslowych:

| bylo | jest |
|---|---|
| pasy odblaskowe na calej dlugosci | **jeden waski pas** tuz pod glowica |
| jasna stalowa kopulka | **czarna plaska glowica** z fazowana krawedzia |
| gruby, przysadzisty korpus | **smukly walec** — proporcje mniej wiecej 1:4,5 |
| pierscien LED dookola | **trzy szczeliny sygnalizacyjne** w plaszczu |
| kolnierz jak rura | **okragla plyta bazowa** wpuszczona w nawierzchnie |
| gladka stal | delikatne rysy **szczotkowania** wzdluz korpusu |

Poswiata LED przeniesiona za korpus — swiatlo rozlewa sie wokol slupka,
zamiast klasc ciemna smuge na stali.

Ikona programu przerysowana tak samo.

## Zmiana nazwy w wersji 4.2

Program nazywal sie wczesniej Szlaban AWF. Zmienilo sie:

| | bylo | jest |
|---|---|---|
| Nazwa | Szlaban AWF | ZAPORA-AWF |
| Plik | Szlaban-AWF.exe | ZAPORA-AWF.exe |
| Instalator | Szlaban-AWF-Instalator | ZAPORA-AWF-Instalator |
| Kod zrodlowy | szlaban_wizual.py | zapora_awf.py |
| Katalog danych | %APPDATA%\AWFGSM | %APPDATA%\ZAPORA-AWF |
| Plik bazy | wizual.json | baza.json |
| Ikona | ramie szlabanu | trzy slupki blokujace |

**Twoje dane sie nie zgubia.** Przy pierwszym uruchomieniu program sam przeniesie
baze numerow, historie wjazdow i logo ze starego katalogu do nowego.
Stary katalog zostaje nietkniety — mozesz go skasowac recznie, gdy sprawdzisz,
ze wszystko jest na miejscu. PIN pozostaje ten sam.

Jesli masz juz zainstalowana poprzednia wersje, nowy instalator ja **zastapi**
(ten sam identyfikator instalacji), a skrot w Menu Start zmieni nazwe.

## NOWE w v4.1 — SLUPKI CHOWANE W JEZDNIE

Domyslna przegroda to teraz **slupki blokujace chowane w jezdnie** (bollardy),
a nie szlaban. Trzy slupki w poprzek wjazdu, kazdy:

- korpus ze stali z cieniowaniem walcowym — swiatlo pada z lewej gory
- trzy pasy odblaskowe (czerwony / bialy / czerwony), ktore **znikaja w jezdni**
  razem z opadajacym slupkiem
- kolnierz montazowy wpuszczony w nawierzchnie
- pierscien LED na glowicy: **czerwony** gdy blokuje, **zolty migajacy** podczas
  ruchu, **zielony** gdy przejazd wolny — z poswiata na jezdni
- cien wydluzajacy sie wraz z wysokoscia slupka
- po schowaniu zostaje tylko plaska pokrywa rowno z jezdnia
- znak zakazu wjazdu przy krawedzi gasnie, gdy przejazd zostaje zwolniony

Ruch jest **wolniejszy niz szlabanu** — okolo 2 sekund w dol i 2 w gore,
tak jak pracuje sila hydrauliczna w prawdziwym slupku.

Stany na ekranie sa nazwane wlasciwie: SLUPKI PODNIESIONE — BLOKADA,
OPUSZCZANIE SLUPKOW, SLUPKI OPUSZCZONE — PRZEJAZD, PODNOSZENIE SLUPKOW.

Szlaban i brama przesuwna nadal sa dostepne — wybierasz w ustawieniach modulu,
pole **Rodzaj przegrody**.

## MODULY, PRZEKAZNIK, HARMONOGRAM

Nadal wszystko dziala jako **symulacja** — zaden modul nie jest jeszcze podpiety.
Ale cala konfiguracja jest juz prawdziwa i zapisywana, wiec po kupieniu sprzetu
zostaje tylko podlaczenie.

### Zakladka MODULY I KARTY SIM

Lista obiektow — kazdy modul to jedna brama. Dla kazdego ustawiasz:

| Ustawienie | Co robi |
|---|---|
| Nazwa obiektu | np. Brama glowna AWF |
| Numer karty SIM | na ten numer beda szly komendy do modulu |
| Haslo modulu | fabrycznie zwykle 1234 |
| Typ modulu | RTU5024, Ropam, Elmes, Roger/Satel, inny |
| Tryb przekaznika | **impuls** (brama sama sie zamyka) albo **stan zalaczony** (trzyma otwarte) |
| Dlugosc impulsu | w milisekundach, 100-5000 |
| Czas otwarcia | ile sekund brama zostaje otwarta |
| Zwloka zamykania | opoznienie przed startem zamykania |
| Autozamykanie | wlaczone / wylaczone |
| Wyglad | szlaban albo brama przesuwna |

Te ustawienia **dzialaja juz teraz w animacji**. Ustawisz czas otwarcia na 15 sekund
— na ekranie zobaczysz odliczanie AUTOZAMYKANIE ZA 15 s. Wylaczysz autozamykanie
— brama zostanie otwarta az klikniesz Zamknij.

Przelaczanie miedzy obiektami jest nad scena w zakladce Podglad.

### Harmonogram dostepu — przy kazdym numerze

W oknie edycji numeru doszla sekcja HARMONOGRAM DOSTEPU:

- **dni tygodnia** — siedem checkboxow, np. tylko pn-pt dla dostawcy
- **godziny od-do** — obsluguje tez zakres przez polnoc, np. 22:00-06:00 dla nocnej zmiany
- **wazny do** — data wygasniecia uprawnienia, np. koniec umowy; puste = bezterminowo
- **numer aktywny** — odznaczenie blokuje wjazd natychmiast, bez kasowania z listy

Na liscie widac kolumne HARMONOGRAM (np. `pn-pt  06:00-18:00`) i STAN, ktory
pokazuje na biezaco czy ta osoba wjedzie **w tej chwili**:
zielone `wpuszcza`, pomaranczowe `poza godz.`, czerwone `ZABLOKOWANY`.

### Odmowa dostepu w animacji

Jesli symulujesz przejazd osoby, ktora akurat nie ma uprawnienia — auto podjezdza,
na ekranie zapala sie czerwone **DOSTEP ZABLOKOWANY** z konkretnym powodem
(np. `dzis (sobota) poza harmonogramem`), szlaban **sie nie podnosi**,
a auto wycofuje. Odmowa trafia do historii tak samo jak wjazd.

## HISTORIA I RAPORTY

Drugi widok (przelacznik u gory okna): **kto i kiedy otwieral brame**.
Kazde otwarcie zapisuje sie trwale na dysku — po zamknieciu programu nic nie ginie.

**Piec kafelkow na gorze:** dzisiaj / ostatnie 7 dni / ten miesiac / lacznie /
kto najczesciej.

**Filtry:** wybor kierowcy z listy + zakres dat (RRRR-MM-DD).
Enter w polu daty od razu filtruje. Przycisk "Wyczysc filtry" wraca do calosci.

**Tabela** — LP, data, godzina, kierowca, telefon, sposob otwarcia.
Reczne otwarcia sa wyroznione na pomaranczowo, zeby odroznic je od wjazdow z telefonu.

**Raport do wydruku** — generuje gotowa strone HTML i otwiera ja w przegladarce:
naglowek z zakresem dat, kafelki podsumowania (liczba otwarc, ile osob,
godzina szczytu ruchu, kto najczesciej), ranking wjazdow z paskami udzialu
i pelna lista zdarzen. Ctrl+P i masz papier dla klienta albo wspolnoty.

**Eksport CSV** — to co widac po filtrze, srednikami, w kodowaniu ktore Excel
otwiera bez kombinowania.

W widoku Podgladu lista numerow ma teraz dwie dodatkowe kolumny:
**WJAZDOW** (licznik) i **OSTATNIO** (data i godzina ostatniego wjazdu),
a nad lista widac ostatnie otwarcie w calym systemie.

Usuniecie osoby z listy **nie kasuje** jej historii — raport za zeszly miesiac
dalej sie zgadza.

## Lista numerow

Dodawanie, edycja (albo dwuklik w wierszu), kasowanie z potwierdzeniem.
Numery normalizuja sie same: `601234567`, `601-234-567`, `0048601234567`
-> wszystko lezy jako `+48601234567`.

**Wpusc zaznaczonego** — odpala przejazd z danymi wybranej osoby na HUD.

Panel zdarzen po prawej loguje kazda akcje z godzina.

Dane: `%APPDATA%\ZAPORA-AWF\baza.json` (numery + historia)
Raport: `%APPDATA%\ZAPORA-AWF\raport.html`

## Uruchomienie

Masz Pythona: `python zapora_awf.py`
Chcesz .exe: kliknij `build-instalator.bat` -> `dist\Szlaban-WIZUAL.exe`
