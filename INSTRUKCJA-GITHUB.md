# Jak zbudowac INSTALATOR na GitHubie — krok po kroku

Nie musisz nic instalowac na komputerze. GitHub zbuduje aplikacje za Ciebie
na swoim Windowsie i da gotowy plik do pobrania.

Jestes zalogowany jako **superdarco78** — wszystko robisz w przegladarce.

---

## KROK 1 — Rozpakuj paczke

Pobrany plik `ZAPORA-AWF-v4.2.zip` -> prawy klik -> **Wyodrebnij wszystko**.
Powstanie folder z plikami. To wlasnie te pliki beda szly na GitHub:

```
zapora_awf.py           <- program
instalator.iss              <- przepis na instalator
ikona.ico                   <- ikona
logo.png                    <- logo w oknie i na ekranie logowania
build-instalator.bat        <- (tylko gdy budujesz u siebie)
.github/workflows/build.yml <- przepis dla GitHuba
```

**UWAGA — folder `.github` jest UKRYTY.**
W Eksploratorze wejdz w zakladke **Widok** -> **Pokaz** -> zaznacz
**Ukryte elementy**. Bez tego go nie zobaczysz, a bez niego GitHub nic nie zbuduje.

---

## KROK 2 — Zaloz repozytorium

1. Na github.com kliknij zielony przycisk **New** (po lewej, nad lista repozytoriow)
2. **Repository name:** `zapora-awf`
3. Zaznacz **Private** (zeby nikt obcy nie widzial)
4. Kliknij **Create repository**

---

## KROK 3 — Wrzuc pliki

Na nowej, pustej stronie repozytorium kliknij link
**uploading an existing file** (albo przycisk **Add file** -> **Upload files**).

Teraz **przeciagnij myszka caly rozpakowany folder** na pole "Drag files here".
Przeciagniecie folderu jest wazne — zachowa strukture `.github/workflows/`.
Jesli przeciagniesz same pliki bez folderu, GitHub nie znajdzie przepisu.

Na dole strony kliknij zielony **Commit changes**.

Sprawdz czy na liscie plikow widnieje pozycja **.github** — jesli tak, jest dobrze.

---

## KROK 4 — Uruchom budowanie

1. Na gorze repozytorium kliknij zakladke **Actions**
2. Jesli pojawi sie zolty komunikat o workflow — kliknij
   **I understand my workflows, go ahead and enable them**
3. Po lewej kliknij **Buduj ZAPORA-AWF**
4. Po prawej rozwin **Run workflow** -> zielony przycisk **Run workflow**

Odswiez strone. Pojawi sie wpis z zoltym kolkiem (trwa) — po okolo 2 minutach
zmieni sie w **zielony ptaszek**.

---

## KROK 5 — Pobierz gotowy plik

Kliknij w ten zielony wpis. Zjedz na sam dol strony, do sekcji **Artifacts**.
Sa tam DWIE paczki — pobierz ta ktora Ci pasuje:

**INSTALATOR-ZAPORA-AWF** — w srodku `ZAPORA-AWF-Instalator-v4.2.exe`.
Normalny kreator instalacji: klikasz Dalej, Dalej, Zainstaluj.
Program laduje w Menu Start, opcjonalnie ikona na pulpicie,
odinstalowanie przez Panel sterowania. **To jest to, o co Ci chodzilo.**

**PRZENOSNA-ZAPORA-AWF** — sam `ZAPORA-AWF.exe`, bez instalacji.
Na pendrive albo do szybkiego pokazania klientowi.

**PIN fabryczny: 1234** — zmien po pierwszym uruchomieniu.

### Co robi instalator

- pyta o katalog docelowy (domyslnie Program Files)
- tworzy skroty: Menu Start, opcjonalnie pulpit, opcjonalnie autostart Windows
- wpisuje program do listy w Panelu sterowania
- przy odinstalowaniu **pyta, czy skasowac rowniez baze numerow i historie**
  — wybierz Nie, jesli tylko robisz aktualizacje
- nie wymaga hasla administratora (instaluje sie dla biezacego uzytkownika)
- kolejna wersja nadpisze poprzednia zamiast instalowac sie obok

---

## Co dalej — kazda zmiana buduje sie sama

Od tej pory nie musisz juz klikac Run workflow.
Wystarczy, ze podmienisz plik w repozytorium
(**Add file** -> **Upload files**, wrzucasz nowa wersje) — GitHub sam
uruchomi budowanie i po 2 minutach nowy .exe czeka w Actions -> Artifacts.

---

## Jesli cos pojdzie nie tak

**Czerwony krzyzyk zamiast ptaszka** — kliknij w niego, potem w krok
oznaczony na czerwono. Skopiuj tekst bledu i przeslij mi.

**Zakladka Actions pusta / brak "Buduj ZAPORA-AWF"** — nie wgral sie folder `.github`.
Wroc do KROKU 3 i przeciagnij caly folder, nie pojedyncze pliki.

**"Windows chronil Twoj komputer" przy uruchomieniu .exe** — kliknij
**Wiecej informacji** -> **Uruchom mimo to**. To normalne dla kazdego programu
bez platnego certyfikatu, nie oznacza wirusa.

**Artifacts znikaja po 90 dniach** — to limit GitHuba. Pobierz plik i zachowaj
u siebie, albo po prostu uruchom budowanie ponownie.

---

## Wymiana logo na wlasne

**Sposob szybki (bez przebudowywania):** wrzuc swoj plik pod nazwa `logo.png`
do folderu `%APPDATA%\ZAPORA-AWF` (wklej te sciezke w pasek adresu Eksploratora).
Program szuka logo najpierw wlasnie tam — wystarczy zamknac i otworzyc aplikacje.
Dziala tez na komputerze klienta, bez ruszania GitHuba.

**Sposob docelowy:** podmien `logo.png` w repozytorium (Add file -> Upload files,
ta sama nazwa). Wtedy logo bedzie juz wbudowane w instalator.

Najlepiej obrazek o wysokosci okolo 50-100 pikseli z przezroczystym tlem.

Nazwe instytucji i podtytul zmieniasz w pliku `baza.json`
(folder `%APPDATA%\ZAPORA-AWF`) w sekcji `marka`.
