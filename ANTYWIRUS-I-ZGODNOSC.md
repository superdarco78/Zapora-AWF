# ZAPORA-AWF — zgodnosc z Windows 10 / 11 i ostrzezenia antywirusa

## Zgodnosc — zalatwione w kodzie

| Co | Jak rozwiazane |
|---|---|
| Windows 10 i 11 (64-bit) | manifest z deklaracja zgodnosci dla Win 7/8/8.1/10/11 |
| Skalowanie ekranu 125% / 150% | swiadomosc DPI — tekst ostry, nie rozmazany |
| Laptop 1366x768 | okno i scena same sie zmniejszaja do rozdzielczosci |
| Monitor 4K | czcionki rosna, z limitem zeby uklad sie nie rozjechal |
| Brak praw administratora | program instaluje sie i dziala jako zwykly uzytkownik |
| Dane na koncie uzytkownika | zapis do %APPDATA%, nie do Program Files |

Wymagany jest Windows 64-bitowy. Wersje 32-bitowe (bardzo stare komputery)
nie sa obslugiwane.

---

## Ostrzezenia antywirusa — co da sie zrobic, a czego nie

Powiem wprost: **calkowicie usunac ostrzezenia da sie tylko kupujac certyfikat
podpisu cyfrowego.** Wszystko inne to zmniejszanie ryzyka. Ponizej co juz zrobilem
i co mozesz zrobic dalej.

### Zrobione w kodzie

**Rezygnacja z pliku jednoplikowego (`--onefile`)**
To byla najwazniejsza zmiana. Wersja jednoplikowa przy kazdym starcie rozpakowuje
sie do folderu tymczasowego i stamtad uruchamia — to zachowanie jest identyczne
z tym, co robi wiele realnych zlosliwych programow, i wlasnie ono najczesciej
wywoluje alarm. Teraz aplikacja to normalny folder z plikiem .exe i bibliotekami,
schowany w instalatorze. Uzytkownik i tak widzi jeden plik do kliknięcia.

**Wylaczone pakowanie UPX** (`--noupx`)
Kompresja UPX zmniejsza plik, ale jest klasycznym sygnalem ostrzegawczym dla
skanerow — uzywa jej mnostwo szkodliwego oprogramowania, zeby ukryc zawartosc.

**Wypelniona metryczka pliku** (`wersja.txt`)
Producent, nazwa produktu, wersja, prawa autorskie. Widac to w Wlasciwosciach
pliku, zakladka Szczegoly. Pusta metryczka podnosi podejrzliwosc heurystyki.

**Manifest z poziomem `asInvoker`**
Program nie prosi o uprawnienia administratora, bo ich nie potrzebuje.
Programy proszace o administratora bez powodu sa oceniane surowiej.

### Co to daje w praktyce

Falszywe alarmy zwyklych antywirusow (Avast, AVG, Bitdefender, Kaspersky)
robia sie rzadkie. Windows Defender zwykle przepuszcza taki plik bez awantury.

**Czego to NIE usuwa:** przy pierwszym pobraniu z internetu Windows pokaze
niebieski ekran **"System Windows ochronil Twoj komputer"**. To nie jest wykrycie
wirusa — to informacja, ze plik nie ma podpisu i Microsoft go jeszcze nie zna.
Klikasz **Wiecej informacji** -> **Uruchom mimo to**. Kazdy niepodpisany program
na swiecie tak ma.

---

## Rozwiazanie docelowe — certyfikat podpisu cyfrowego

Podpisany plik nie pokazuje ostrzezenia o nieznanym wydawcy, a we wlasciwosciach
pliku widnieje Twoja nazwa jako wydawcy. Dla firmy montujacej systemy u klientow
to tez po prostu lepiej wyglada.

**Certum (polska firma, Asseco)** ma najtansza sciezke — certyfikat
Open Source Code Signing. <cite index="1-1">Certum podaje, ze certyfikat jest zaufany przez Microsoft i wspiera budowanie reputacji w filtrze SmartScreen, a osoby pobierajace podpisane oprogramowanie nie zobacza ostrzezen o nieznanym wydawcy</cite>. U resellerow <cite index="3-1">cena zaczyna sie w okolicach 50 dolarow</cite> — sprawdz aktualna na shop.certum.eu, bo sie zmienia.

Rzeczy, o ktorych warto wiedziec zanim kupisz:

- klucz musi siedziec na tokenie USB albo w chmurze (Certum SimplySign) —
  tak nakazuja obecne przepisy branzowe, nie da sie tego obejsc
- weryfikacja tozsamosci trwa zwykle kilka dni roboczych
- certyfikat zwykly (OV) buduje reputacje w SmartScreen stopniowo, przez
  kilkadziesiat pobran; certyfikat EV daje ja od razu, ale kosztuje kilkakrotnie
  wiecej
- wersja Open Source jest tania, ale wymaga, zeby kod byl publicznie dostepny —
  jesli repozytorium ma zostac prywatne, potrzebujesz zwyklego certyfikatu firmowego

Gdy juz go zdobedziesz, podpisywanie dokladamy do GitHuba jako jeden dodatkowy
krok — powiedz wtedy, dopisze.

---

## Gdy antywirus mimo wszystko zglosi falszywy alarm

1. **Zglos to producentowi antywirusa** — to darmowe i zwykle poprawiaja w 1-3 dni:
   - Microsoft Defender: `microsoft.com/wdsi/filesubmission` -> Software developer
   - inni producenci maja podobne formularze pod haslem "false positive"

2. **Doraznie u klienta** — dodaj folder programu do wyjatkow w antywirusie.
   Robisz to swiadomie, bo wiesz co to za plik.

3. **Sprawdz obiektywnie** — wrzuc plik na `virustotal.com`. Jesli zglasza go
   1-3 skanery z 70, to typowy falszywy alarm dla programow zbudowanych
   PyInstallerem. Jesli zglasza kilkanascie — napisz mi, cos jest nie tak.

4. **Nie zmieniaj nazwy pliku ani nie kompresuj go dodatkowo** — to pogarsza
   sprawe, nie poprawia.
