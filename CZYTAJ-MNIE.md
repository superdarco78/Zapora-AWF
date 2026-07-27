# ZAPORA-AWF v5.0

Akademia Wychowania Fizycznego Jozefa Pilsudskiego w Warszawie — Straz Akademicka.
System kontroli wjazdu: zapora slupkowa ze slupkami chowanymi w jezdnie.

## NOWE w v5.0 — scena z prawdziwego zdjecia wjazdu

Podglad nie jest juz rysunkiem. Tlem jest **fotografia Waszego wjazdu**,
a slupki, ktore sie chowaja, sa **wyciete z tego samego zdjecia**.
Zadne piksele nie sa dorysowywane — kazda klatka animacji to ten sam wycinek
fotografii, tylko krotszy.

### Jak to zostalo przygotowane

1. **Wyciecie slupkow** — cztery slupki BFT wraz z plytami podstawy, z maska
   w ksztalcie kolumny (prawdziwy slupek jest rownym walcem, wiec rowna
   krawedz cieca jest blizsza prawdy niz obrys po kolorze, ktory wychodzil
   poszarpany przez prety ogrodzenia).
2. **Zaklejenie dziur** — program przeszukuje kilkaset fragmentow bruku wokol
   i wybiera ten o najlepiej pasujacej jasnosci i rozrzucie, a nastepnie
   **wyrownuje mu kolor kanal po kanale** do bruku dookola.
3. **Kontrola** — najpierw zmierzony zostal naturalny rozrzut samego bruku
   (26 stopni jasnosci), a potem slad po kazdym slupku. Wyniki: 22, 22, 10 i 6.
   Wszystkie ponizej naturalnego rozrzutu, czyli slad jest mniejszy niz roznica
   miedzy dwiema sasiednimi kostkami.

Duzy slupek CAME po prawej i biale kamienne w tle pozostaja nieruchome,
tak jak w rzeczywistosci — chowaja sie **tylko te cztery srodkowe**.

### Panele i przyciski na zdjeciu

Panele informacyjne sa **naprawde przezroczyste** — widac przez nie bruk.
Tkinter nie potrafi przezroczystosci na plotnie, wiec panele sa wtapiane
w fotografie jeszcze przed wyswietleniem.

Na dolnym pasku sa trzy przyciski wtopione w obraz:
**SYMULUJ PRZEJAZD**, **OTWORZ**, **ZAMKNIJ** — klikalne bezposrednio na zdjeciu.

Stan wyswietla sie w prawym gornym rogu razem z imieniem i numerem
osoby wjezdzajacej, a przy odmowie — z powodem.

### Powrot do sceny rysowanej

W ustawieniach obiektu jest przelacznik **„Scena z prawdziwego zdjecia wjazdu"**.
Po odznaczeniu wraca rysowana scena ze slupkami, szlabanem albo brama przesuwna.

## NOWE w v4.8 — osobna zakladka STEROWNIK

Uklad odwzorowuje konfigurator modulu GSM: karty jedna pod druga,
te same nazwy pol, te same przyciski.

### Polaczenie
Przycisk **Polacz / Rozlacz**, obok **wskaznik sily sygnalu** (piec slupkow
i wartosc procentowa) oraz stan tekstowy. Bez podlaczonego modulu dziala
jako **symulacja** — jest to wprost napisane na ekranie, zeby nikt sie nie pomylil
przy pokazie.

Checkbox **Pokaz logi** rozwija na dole okno z logiem operacji, ze znacznikami czasu.

### Odczyt / zapis danych do sterownika
Cztery przyciski w ukladzie 2x2:

| | |
|---|---|
| **Pobierz ze sterownika** | **Wgraj do sterownika** |
| **Zapis kopii danych** | **Odczyt kopii danych** |

Dwa gorne czekaja na sprzet — pokazuja, co i na jaki numer SIM zostaloby wyslane.
Dwa dolne **dzialaja juz teraz**: zapis i odczyt pelnej kopii ustawien do pliku JSON.

### Kod dostepu i tryb sterowania
Kod wyswietlany duza czcionka, tryb do wyboru: **CLIP** (otwiera samo polaczenie),
**SMS**, **CLIP+SMS**.

### Tryb pracy i konfiguracja wyjscia
**Prywatny** — wpuszcza tylko numery z listy.
**Publiczny** — wpuszcza kazdy numer. Pod przelacznikiem widac opis wybranego trybu.

Wyjscie: **Zalaczenie (s)** z polem na liczbe sekund albo **Toggle (ON/OFF)**.

**Wszystkie zmiany zapisuja sie od razu**, bez przycisku Zapisz, i od razu
wplywaja na symulacje — po wlaczeniu trybu publicznego zablokowany numer
zostanie wpuszczony, a w historii pojawi sie stosowna adnotacja.

## NOWE w v4.7 — opcje jak w konfiguratorze sterownika

Zakladka **MODULY I KARTY SIM** ma teraz po prawej panel **Sterownik**,
odwzorowujacy uklad typowego konfiguratora modulu GSM.

### Polaczenie
Stan lacznosci ze sterownikiem. W wersji demonstracyjnej pokazuje
`brak — tryb demo`; po podlaczeniu modulu bedzie tu sila sygnalu GSM.

### Odczyt / zapis danych do sterownika
**Pobierz ze sterownika** i **Wgraj do sterownika** — dwa przyciski,
ktore po podlaczeniu sprzetu beda przenosic ustawienia miedzy programem
a modulem. Teraz pokazuja, co dokladnie zostaloby wyslane i na jaki numer SIM.

### Kopia zapasowa ustawien — **dziala juz teraz**
**Zapis kopii danych** zapisuje do pliku JSON komplet: obiekty, numery,
harmonogramy, historie wjazdow i ustawienia sterownika.
**Odczyt kopii danych** wczytuje taki plik z powrotem, po potwierdzeniu
ile obiektow i wpisow zostanie przywroconych.

To najprostszy sposob przeniesienia wszystkiego na inny komputer
albo zabezpieczenia sie przed pomylka.

### Nowe ustawienia modulu

W oknie edycji obiektu doszla sekcja **STEROWNIK GSM**:

| Ustawienie | Znaczenie |
|---|---|
| Tryb sterowania | CLIP (otwiera samo polaczenie) / SMS / CLIP+SMS |
| Tryb pracy | **prywatny** — wpuszcza tylko numery z listy<br>**publiczny** — wpuszcza kazdy numer |
| Zalaczenie (s) | dlugosc zalaczenia wyjscia w sekundach |

**Tryb publiczny dziala na zywo** — po jego wlaczeniu symulacja wpuszcza
rowniez numery zablokowane i te poza harmonogramem, z adnotacja w historii.
Kolumny w tabeli obiektow pokazuja teraz tryb sterowania i tryb pracy.

## POPRAWKI w v4.6 — dwa bledy z v4.5

**1. Program nie uruchamial sie wcale.**
W funkcji rysujacej scene byla uzyta zmienna, ktora nigdy nie zostala zdefiniowana.
Efekt: okno wywalalo sie natychmiast po zalogowaniu komunikatem
`NameError: name 'p' is not defined`.

**2. Domyslnie rysowal sie szlaban zamiast slupkow.**
Wczesniejsza zmiana domyslnego rodzaju przegrody nie zadzialala — podmiana
nie trafila w tekst i przeszla bez sladu. Nowe instalacje pokazywaly szlaban.

Bazy zalozone wczesniej dostana jednorazowa korekte na slupki. Jesli sam
wybrales rodzaj przegrody w ustawieniach modulu, Twoj wybor zostaje.

### Skad sie wziely

Do tej wersji sprawdzalem kod tylko pod katem skladni, a wyglad renderowalem
osobnym skryptem odwzorowujacym rysowanie. Zaden z tych sposobow nie uruchamia
prawdziwego okna, wiec oba bledy przeszly niezauwazone.

Od v4.6 kazda wersja jest **faktycznie uruchamiana** na wirtualnym ekranie:
otwarcie okna, logowanie PIN-em, przerysowanie sceny we wszystkich stanach
(3 rodzaje przegrody x 2 motywy x 5 pozycji x 10 faz = 300 kombinacji),
przelaczanie zakladek i motywu, symulacja przejazdu i odmowy dostepu,
generowanie raportu. Do tego analiza statyczna wykrywajaca nieistniejace nazwy.

## NOWE w v4.5

### Slupki chowaja sie calkowicie

Wczesniej slupek w koncowej fazie chowania nachodzil na nawierzchnie —
glowica i pas odblaskowy byly rysowane na jezdni, zamiast pod nia.
Zmieniona zostala kolejnosc rysowania: **najpierw korpusy, potem jezdnia na nich**,
a na samym koncu plyty bazowe i cienie. Slupek naprawde wchodzi w grunt.

Po pelnym schowaniu zostaje wylacznie plaska pokrywa rowno z nawierzchnia —
tak jak w rzeczywistosci. W trakcie chowania widac ciemna szczeline wokol
korpusu wchodzacego w otwor.

### Tryb jasny i ciemny

Przycisk **Tryb jasny / Tryb ciemny** w prawym gornym rogu okna.
Przelacza cala aplikacje razem ze scena:

| | tryb ciemny | tryb jasny |
|---|---|---|
| Interfejs | granatowy | bialy |
| Scena | zmierzch, zapalone latarnie | dzien, latarnie zgaszone |
| Nawierzchnia | ciemny asfalt | jasny beton |
| Stal slupkow | chlodna, kontrastowa | jasna, matowa |
| Cienie | glebokie | miekkie |

Wybor zapisuje sie w bazie — program uruchomi sie w tym trybie, w ktorym go zostawisz.

Kontrast tekstu sprawdzony wedlug WCAG w obu trybach; kolor akcentu
w trybie jasnym zostal przyciemniony, bo pierwotny mial za slaby kontrast na bieli.

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
