# -*- coding: utf-8 -*-
"""
ZAPORA-AWF
Wersja skupiona na wygladzie: realistyczna animacja szlabanu + lista numerow.
Bez modemu, bez SMS-ow. Czysty Python + tkinter.
"""

import csv
import hashlib
import json
import math
import os
import re
import sys
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk

APP = "ZAPORA-AWF"
VER = "5.0"
DATA_WYD = "27.07.2026"

# paleta
MOTYWY = {
    "ciemny": {
        "BG": "#0e1217", "BG2": "#161c24", "BG3": "#212a35",
        "FG": "#e8eef6", "DIM": "#7d8b9c", "ACC": "#3b8ff5",
        "OK": "#37c76a", "WARN": "#e8a33d",
        "scena": {
            "niebo1": "#0a1220", "niebo2": "#1d2f4a", "horyzont": "#3a3550",
            "jezdnia1": "#252a31", "jezdnia2": "#181c22", "krawedz": "#39424e",
            "krawez": "#333a44", "pasy": "#4a5460", "plot": "#121820",
            "slup_latarni": "#141a22", "latarnia": True,
            "cien": "#0e1218", "plyta": "#333a44", "plyta2": "#262c34",
            "stal1": "#59636f", "stal2": "#eef3f8", "stal_lewa": "#7a8794",
            "rysy": "#8d99a6", "glowica": "#181d24", "glowica2": "#2b323b",
            "tlo_hud": "#0d141d", "ramka_hud": "#243040", "alarm": "#e05a5f",
        },
    },
    "jasny": {
        "BG": "#f2f5f9", "BG2": "#ffffff", "BG3": "#e4e9f0",
        "FG": "#18212c", "DIM": "#5b6a7d", "ACC": "#1657b8",
        "OK": "#127a3c", "WARN": "#96610d",
        "scena": {
            "niebo1": "#8cb8e4", "niebo2": "#cfe3f5", "horyzont": "#eaf1f8",
            "jezdnia1": "#9ba4ae", "jezdnia2": "#7f8892", "krawedz": "#6d7681",
            "krawez": "#b6bec7", "pasy": "#eef2f6", "plot": "#a9b4c0",
            "slup_latarni": "#8c97a3", "latarnia": False,
            "cien": "#6d7883", "plyta": "#77818c", "plyta2": "#5d6771",
            "stal1": "#8e99a5", "stal2": "#ffffff", "stal_lewa": "#b3bcc6",
            "rysy": "#c3cbd4", "glowica": "#3a424c", "glowica2": "#59636f",
            "tlo_hud": "#ffffff", "ramka_hud": "#c9d2dc", "alarm": "#bf2a30",
        },
    },
}

BG, BG2, BG3 = "#0e1217", "#161c24", "#212a35"
FG, DIM, ACC = "#e8eef6", "#7d8b9c", "#3b8ff5"
OK, WARN = "#37c76a", "#e8a33d"
SC = MOTYWY["ciemny"]["scena"]


def ustaw_motyw(nazwa):
    """Przestawia globalna palete kolorow."""
    global BG, BG2, BG3, FG, DIM, ACC, OK, WARN, SC
    m = MOTYWY.get(nazwa, MOTYWY["ciemny"])
    BG, BG2, BG3 = m["BG"], m["BG2"], m["BG3"]
    FG, DIM, ACC = m["FG"], m["DIM"], m["ACC"]
    OK, WARN = m["OK"], m["WARN"]
    SC = m["scena"]


def kat_dir():
    """Katalog danych. Przy pierwszym starcie przenosi baze ze starej nazwy."""
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, "ZAPORA-AWF")
    os.makedirs(d, exist_ok=True)
    stary = os.path.join(base, "Monter24hGSM")   # jedyny slad po starej nazwie:
    # sluzy wylacznie przeniesieniu bazy z wersji <=4.1, mozna usunac po migracji
    if os.path.isdir(stary):
        for plik, docel in (("wizual.json", "baza.json"), ("logo.png", "logo.png"),
                            ("log.txt", "log.txt")):
            zr, do = os.path.join(stary, plik), os.path.join(d, docel)
            if os.path.exists(zr) and not os.path.exists(do):
                try:
                    with open(zr, "rb") as a, open(do, "wb") as b:
                        b.write(a.read())
                except Exception:
                    pass
    return d


PLIK = os.path.join(kat_dir(), "baza.json")
SOL = "zapora-awf-2026"
SOL_STARA = "monter24h-szlaban"      # tylko do uznania PIN-u z wersji <=4.3


def zasob(nazwa):
    """Szuka pliku po kolei: katalog danych uzytkownika -> obok programu -> w srodku .exe.

    Dzieki temu logo.png mozna podmienic bez przebudowywania aplikacji —
    wystarczy wrzucic je do %APPDATA%\\ZAPORA-AWF.
    """
    kandydaci = [os.path.join(kat_dir(), nazwa)]
    if getattr(sys, "frozen", False):
        kandydaci.append(os.path.join(os.path.dirname(sys.executable), nazwa))
        mei = getattr(sys, "_MEIPASS", "")
        if mei:
            kandydaci.append(os.path.join(mei, nazwa))
    else:
        kandydaci.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), nazwa))
    for k in kandydaci:
        if os.path.exists(k):
            return k
    return ""


def wlacz_dpi():
    """Wylacza rozmazywanie okna przez Windows przy skalowaniu ekranu.

    Bez tego na laptopie ustawionym na 125% lub 150% cala aplikacja jest
    rozciagana jak powiekszony obrazek — tekst wychodzi nieostry.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)   # per-monitor
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()        # starsze Windowsy
    except Exception:
        pass


def dpi_systemu():
    if sys.platform != "win32":
        return 96
    try:
        import ctypes
        return int(ctypes.windll.user32.GetDpiForSystem())
    except Exception:
        return 96


DNI = ["pn", "wt", "sr", "cz", "pt", "so", "nd"]
DNI_PL = {"pn": "poniedzialek", "wt": "wtorek", "sr": "sroda", "cz": "czwartek",
          "pt": "piatek", "so": "sobota", "nd": "niedziela"}

TYPY_MODULOW = ["RTU5024 / King Pigeon", "Ropam BasicGSM", "Elmes GSM",
                "Roger / Satel", "Inny"]


def nowy_modul():
    return {"nazwa": "Brama glowna", "sim": "", "typ": TYPY_MODULOW[0],
            "haslo": "1234", "tryb": "impuls", "impuls_ms": 500,
            "czas_otwarcia": 8, "autozamykanie": True, "opoznienie": 2,
            "wyglad": "slupki", "zdjecie": True, "tryb_sterowania": "CLIP+SMS",
            "tryb_pracy": "prywatny", "zalaczenie_s": 1, "numery": []}


def sprawdz_dostep(n, teraz=None, modul=None):
    """Czy ten numer ma teraz prawo otworzyc? Zwraca (tak/nie, powod)."""
    teraz = teraz or datetime.now()
    if modul and modul.get("tryb_pracy") == "publiczny":
        return True, "tryb publiczny — wpuszcza kazdy numer"
    if not n.get("aktywny", True):
        return False, "numer zablokowany recznie"
    wd = (n.get("wazny_do") or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", wd) and teraz.strftime("%Y-%m-%d") > wd:
        return False, f"uprawnienie wygaslo {wd}"
    dni = n.get("dni") or list(DNI)
    if DNI[teraz.weekday()] not in dni:
        return False, f"dzis ({DNI_PL[DNI[teraz.weekday()]]}) poza harmonogramem"
    od = n.get("godz_od") or "00:00"
    do = n.get("godz_do") or "23:59"
    t = teraz.strftime("%H:%M")
    if od <= do:
        ok = od <= t <= do
    else:                       # zakres przez polnoc, np. 22:00-06:00
        ok = t >= od or t <= do
    if not ok:
        return False, f"poza godzinami {od}-{do}"
    return True, "uprawniony"


def wczytaj_foto():
    """Material zdjeciowy: prawdziwy wjazd + slupki wyciete z tego samego zdjecia.

    Panele sterowania sa wtapiane w zdjecie z prawdziwa przezroczystoscia,
    bo tkinter sam nie potrafi przezroczystosci na plotnie.
    """
    try:
        from PIL import Image as _Img, ImageDraw as _Draw
        uk = zasob("kiosk-uklad.json")
        tl = zasob("kiosk-tlo.png")
        if not uk or not tl:
            return None
        with open(uk, "r", encoding="utf-8") as f:
            dane = json.load(f)
        tlo = _Img.open(tl).convert("RGB")
        W, H = tlo.size

        # --- przezroczyste panele wtopione w zdjecie ---
        nak = _Img.new("RGBA", (W, H), (0, 0, 0, 0))
        d = _Draw.Draw(nak)
        d.rounded_rectangle([16, 16, 322, 96], radius=12, fill=(8, 14, 22, 155))
        d.rounded_rectangle([W - 348, 16, W - 16, 118], radius=12, fill=(8, 14, 22, 155))
        d.rounded_rectangle([16, H - 74, 470, H - 16], radius=12, fill=(8, 14, 22, 150))
        # trzy przyciski w dolnym pasku
        for x1, x2 in PRZYCISKI_X:
            d.rounded_rectangle([x1, H - 64, x2, H - 26], radius=9,
                                fill=(255, 255, 255, 34), outline=(255, 255, 255, 90))
        dane["_tlo"] = _Img.alpha_composite(tlo.convert("RGBA"), nak).convert("RGB")

        for sl in dane["slupki"]:
            sc = zasob(sl["plik"])
            if not sc:
                return None
            sl["_obraz"] = _Img.open(sc).convert("RGBA")
        return dane
    except Exception:
        return None


PRZYCISKI_X = [(30, 168), (180, 288), (300, 456)]
PRZYCISKI_OPIS = ["SYMULUJ PRZEJAZD", "OTWORZ", "ZAMKNIJ"]


def platform_wersja():
    return ".".join(str(x) for x in sys.version_info[:3])


def hasz_pin(pin, sol=None):
    return hashlib.sha256(((sol or SOL) + str(pin)).encode()).hexdigest()


def pin_pasuje(pin, zapisany):
    """Sprawdza PIN. Uznaje tez skrot z poprzedniej wersji i zwraca nowy do przepisania."""
    if hasz_pin(pin) == zapisany:
        return True, None
    if hashlib.sha256((SOL_STARA + str(pin)).encode()).hexdigest() == zapisany:
        return True, hasz_pin(pin)
    return False, None


def hx(r, g, b):
    return "#%02x%02x%02x" % (max(0, min(255, int(r))), max(0, min(255, int(g))),
                              max(0, min(255, int(b))))


def rgb(c):
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def mix(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    return hx(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def ease(t):
    """Plynne przyspieszenie i hamowanie (smoothstep)."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def norm_tel(nr):
    nr = re.sub(r"[^\d+]", "", (nr or "").strip())
    if not nr:
        return ""
    if nr.startswith("00"):
        nr = "+" + nr[2:]
    if not nr.startswith("+"):
        nr = ("+48" + nr) if len(nr) == 9 else ("+" + nr)
    return nr


def wczytaj():
    try:
        with open(PLIK, "r", encoding="utf-8") as f:
            d = json.load(f)
            d.setdefault("historia", [])
            # migracja z wersji <4.0: plaska lista numerow -> pierwszy modul
            if "moduly" not in d:
                m = nowy_modul()
                m["numery"] = d.pop("numery", [])
                d["moduly"] = [m]
            d.pop("numery", None)
            for m in d["moduly"]:
                for k, v in nowy_modul().items():
                    if k != "numery":
                        m.setdefault(k, v)
                # bazy z wersji <=4.5 mialy blednie ustawiony szlaban jako domyslny;
                # poprawiamy tylko wtedy, gdy uzytkownik nie wybral rodzaju sam
                if not m.get("wyglad_wybrany"):
                    m["wyglad"] = "slupki"
                for n in m.get("numery", []):
                    n.setdefault("aktywny", True)
                    n.setdefault("dni", list(DNI))
                    n.setdefault("godz_od", "00:00")
                    n.setdefault("godz_do", "23:59")
                    n.setdefault("wazny_do", "")
            d.setdefault("pin", hasz_pin("1234"))
            d.setdefault("motyw", "ciemny")
            d.setdefault("marka", {"nazwa": "Straz Akademicka AWF",
                                   "podtytul": "Zapora slupkowa — kontrola wjazdu"})
            return d
    except Exception:
        m = nowy_modul()
        m["sim"] = "+48500100200"
        m["numery"] = [
            {"imie": "Jan Kowalski", "tel": "+48601234567", "uwagi": "mieszkanie 4",
             "aktywny": True, "dni": list(DNI), "godz_od": "00:00",
             "godz_do": "23:59", "wazny_do": ""},
            {"imie": "Anna Nowak", "tel": "+48602345678", "uwagi": "mieszkanie 7",
             "aktywny": True, "dni": list(DNI), "godz_od": "00:00",
             "godz_do": "23:59", "wazny_do": ""},
            {"imie": "Trans-Bud sp. z o.o.", "tel": "+48603456789", "uwagi": "dostawy",
             "aktywny": True, "dni": ["pn", "wt", "sr", "cz", "pt"],
             "godz_od": "06:00", "godz_do": "18:00", "wazny_do": ""},
        ]
        return {"historia": [], "pin": hasz_pin("1234"), "moduly": [m], "motyw": "ciemny",
                "marka": {"nazwa": "Straz Akademicka AWF",
                          "podtytul": "Zapora slupkowa — kontrola wjazdu"}}


def zapisz(d):
    try:
        with open(PLIK, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Blad zapisu", str(e))


# =============================== SCENA ===============================
class Scena(tk.Canvas):
    """Rysuje i animuje szlaban."""

    W, H = 1120, 460
    GY = 380               # poziom jezdni
    PX = 400               # x szafki szlabanu
    ARM = 230              # dlugosc ramienia
    KAT_MAX = 87           # kat otwarcia w stopniach

    def __init__(self, master, on_event=None):
        super().__init__(master, bg=SC["niebo1"], height=self.H,
                         highlightthickness=0, bd=0)
        self.on_event = on_event or (lambda t: None)
        self.postep = 0.0          # 0 = zamkniety, 1 = otwarty
        self.cel = 0.0
        self.faza = "spoczynek"
        self.auto_x = -260.0
        self.kto = ""
        self.tel = ""
        self.t = 0
        self.busy = False
        self.tik = 0
        self.powod = ""
        self.czas_otwarcia = 8      # sekundy, ile brama zostaje otwarta
        self.autozamykanie = True
        self.opoznienie = 2         # sekundy zwloki przed startem zamykania
        self.tryb = "impuls"
        self.odliczanie = 0.0
        self.foto = None            # material zdjeciowy, gdy tryb zdjeciowy wlaczony
        self.nazwa_obiektu = "ZAPORA"
        self.on_przycisk = None
        self.bind("<Button-1>", self.klik_foto)
        self._cache_foto = {}
        self._tk_obrazy = []
        self._petla()

    # ---------- pomocnicze ----------
    def _gradient(self, x0, y0, x1, y1, c1, c2, kroki=48):
        h = (y1 - y0) / kroki
        for i in range(kroki):
            self.create_rectangle(x0, y0 + i * h, x1, y0 + (i + 1) * h + 1,
                                  fill=mix(c1, c2, i / (kroki - 1)), outline="")

    def _poswiata(self, x, y, r, kolor, warstwy=7):
        for i in range(warstwy, 0, -1):
            t = i / warstwy
            self.create_oval(x - r * t, y - r * t, x + r * t, y + r * t,
                             fill=mix("#0a0e14", kolor, (1 - t) ** 1.6), outline="")

    def _obrot(self, px, py, dx, dy, kat):
        """Punkt (dx,dy) w ukladzie ramienia -> wspolrzedne ekranu."""
        c, s = math.cos(kat), math.sin(kat)
        return px + dx * c + dy * s, py - dx * s + dy * c

    # ---------- rysowanie ----------
    def rysuj(self):
        self.delete("all")
        W = max(self.winfo_width(), 900)
        GY = self.GY
        self.tik += 1
        rusza = self.faza in ("otwieranie", "zamykanie")
        mig = rusza and (self.tik // 12) % 2 == 0

        # --- niebo ---
        self._gradient(0, 0, W, GY - 60, SC["niebo1"], SC["niebo2"], 40)
        self._gradient(0, GY - 60, W, GY, SC["niebo2"], SC["horyzont"], 16)
        # latarnie
        for lx in (120, W - 160):
            self.create_line(lx, GY, lx, GY - 190, fill=SC["slup_latarni"], width=5)
            self.create_line(lx, GY - 190, lx + 34, GY - 196,
                             fill=SC["slup_latarni"], width=4)
            if SC["latarnia"]:
                self._poswiata(lx + 36, GY - 194, 46, "#e8a33d", 8)
            else:
                self.create_oval(lx + 26, GY - 200, lx + 46, GY - 188,
                                 fill="#d8dee6", outline=SC["slup_latarni"])
        # plot w tle
        for bx in range(0, W, 46):
            self.create_rectangle(bx, GY - 34, bx + 34, GY - 4,
                                  fill=SC["plot"], outline="")

        # --- jezdnia ---
        self._gradient(0, GY, W, self.H, SC["jezdnia1"], SC["jezdnia2"], 12)
        self.create_line(0, GY, W, GY, fill=SC["krawedz"], width=2)
        for x in range(-30, W, 78):
            self.create_rectangle(x, GY + 46, x + 40, GY + 52,
                                  fill=SC["pasy"], outline="")
        self.create_rectangle(0, GY - 6, W, GY, fill=SC["krawez"], outline="")

        px = self.PX
        p = self.postep
        kat = math.radians(self.postep * self.KAT_MAX)

        # --- wariant zdjeciowy: prawdziwy wjazd ---
        if self.foto:
            self.rysuj_foto(p, mig)
            self.hud(W)
            return

        # --- wariant: slupki chowane w jezdnie ---
        if getattr(self, "vtyp_bramy", "slupki") == "slupki":
            self.rysuj_slupki(px, GY, p, mig)
            self.rysuj_auto(self.auto_x, GY)
            self.hud(W)
            return

        # --- wariant: brama przesuwna ---
        if getattr(self, "vtyp_bramy", "slupki") == "przesuwna":
            self.rysuj_brame(px, GY, p, mig)
            self.rysuj_auto(self.auto_x, GY)
            self.hud(W)
            return

        # --- cien ramienia na jezdni ---
        dl = self.ARM * math.cos(kat)
        if dl > 6:
            self.create_polygon(px + 16, GY + 8, px + 16 + dl, GY + 4,
                                px + 16 + dl, GY + 12, px + 16, GY + 18,
                                fill="#0e1218", outline="")

        # --- fundament + szafka ---
        self.create_rectangle(px - 40, GY - 12, px + 42, GY + 8,
                              fill="#2a3038", outline="#3c444f")
        self._gradient(px - 26, GY - 138, px + 28, GY - 8, "#39424e", "#232a33", 26)
        self.create_rectangle(px - 26, GY - 138, px + 28, GY - 8,
                              outline="#4c5764", width=2)
        self.create_line(px - 26, GY - 104, px + 28, GY - 104, fill="#4c5764")
        self.create_line(px - 26, GY - 46, px + 28, GY - 46, fill="#4c5764")
        # zolto-czarne pasy ostrzegawcze na szafce
        for i in range(5):
            y = GY - 44 + i * 7
            self.create_polygon(px - 24, y + 6, px - 16, y, px + 26, y, px + 18, y + 6,
                                fill="#d9a52c" if i % 2 == 0 else "#1b2028", outline="")
        # logo
        self.create_text(px + 1, GY - 122, text="AWF", fill="#8fa4bd",
                         font=("Segoe UI Semibold", 8))

        # --- lampa ostrzegawcza ---
        lampx, lampy = px + 1, GY - 152
        if mig:
            self._poswiata(lampx, lampy, 38, "#f0a93a", 8)
        self.create_oval(lampx - 11, lampy - 11, lampx + 11, lampy + 11,
                         fill="#f2b544" if mig else "#4a3a1c", outline="#5c6672", width=2)
        self.create_rectangle(lampx - 4, lampy + 9, lampx + 4, GY - 138,
                              fill="#39424e", outline="")

        # --- ramie szlabanu ---
        pivx, pivy = px + 4, GY - 132
        gr = 9  # polgrubosc ramienia
        # przeciwwaga
        cx, cy = self._obrot(pivx, pivy, -34, 0, kat)
        self.create_oval(cx - 15, cy - 15, cx + 15, cy + 15,
                         fill="#2b323b", outline="#454f5c", width=2)
        # segmenty w pasy
        seg = 9
        for i in range(seg):
            t1, t2 = i / seg * self.ARM, (i + 1) / seg * self.ARM
            p1 = self._obrot(pivx, pivy, t1, -gr, kat)
            p2 = self._obrot(pivx, pivy, t2, -gr, kat)
            p3 = self._obrot(pivx, pivy, t2, gr, kat)
            p4 = self._obrot(pivx, pivy, t1, gr, kat)
            kol = "#d93b40" if i % 2 == 0 else "#eef2f7"
            self.create_polygon(p1, p2, p3, p4, fill=kol, outline="#0d1117")
            # odblask u gory ramienia
            q1 = self._obrot(pivx, pivy, t1, -gr + 1, kat)
            q2 = self._obrot(pivx, pivy, t2, -gr + 1, kat)
            self.create_line(q1, q2,
                             fill=mix(kol, "#ffffff", 0.35), width=2)
        # zakonczenie ramienia
        ex, ey = self._obrot(pivx, pivy, self.ARM, 0, kat)
        self.create_oval(ex - gr, ey - gr, ex + gr, ey + gr,
                         fill="#c9d3e0", outline="#0d1117")
        # odblaski
        for t in (0.35, 0.62, 0.88):
            rx, ry = self._obrot(pivx, pivy, self.ARM * t, 0, kat)
            self.create_oval(rx - 3, ry - 3, rx + 3, ry + 3,
                             fill="#ffd66b", outline="")
        # os obrotu
        self.create_oval(pivx - 12, pivy - 12, pivx + 12, pivy + 12,
                         fill="#4a5462", outline="#63707f", width=2)
        self.create_oval(pivx - 4, pivy - 4, pivx + 4, pivy + 4,
                         fill="#1b2028", outline="")

        # --- samochod ---
        self.rysuj_auto(self.auto_x, GY)

        # --- HUD ---
        self.hud(W)

    def rysuj_foto(self, p, mig):
        """Scena z prawdziwego zdjecia wjazdu.

        Kazda klatka to ten sam wycinek zdjecia, tylko krotszy — zadne piksele
        nie sa dorysowywane, wszystkie pochodza z oryginalu.
        """
        from PIL import ImageTk
        self._tk_obrazy = []
        f = self.foto
        W, H = f["_tlo"].size

        if "tlo" not in self._cache_foto:
            self._cache_foto["tlo"] = ImageTk.PhotoImage(f["_tlo"])
        self._tk_obrazy.append(self._cache_foto["tlo"])
        self.create_image(0, 0, image=self._cache_foto["tlo"], anchor="nw")

        # slupki — widoczna zostaje gorna czesc, reszta chowa sie w bruku
        krok = max(0, min(48, int(round((1.0 - p) * 48))))
        for i, sl in enumerate(f["slupki"]):
            widoczne = int(sl["wys"] * krok / 48.0)
            if widoczne < 3:
                continue
            klucz = (i, krok)
            if klucz not in self._cache_foto:
                kadr = sl["_obraz"].crop((0, 0, sl["szer"], widoczne))
                self._cache_foto[klucz] = ImageTk.PhotoImage(kadr)
            obr = self._cache_foto[klucz]
            self._tk_obrazy.append(obr)
            self.create_image(sl["cx"], sl["grunt"] - widoczne, image=obr, anchor="n")

        self.hud_foto(W, H, p, mig)

    def hud_foto(self, W, H, p, mig):
        """Napisy i przyciski na wtopionych panelach."""
        self.create_text(34, 42, text=self.nazwa_obiektu, anchor="w", fill="#f2f6fb",
                         font=("Segoe UI Semibold", 12))
        self.create_text(34, 68, text=datetime.now().strftime("%d.%m.%Y   %H:%M:%S"),
                         anchor="w", fill="#b9c6d6", font=("Consolas", 10))

        stan = {"spoczynek": ("SLUPKI PODNIESIONE", "#e8eef6"),
                "jedzie": ("POJAZD PODJEZDZA", "#e8eef6"),
                "dzwoni": ("POLACZENIE PRZYCHODZACE", "#f2b544"),
                "otwieranie": ("OPUSZCZANIE SLUPKOW", "#4ade80"),
                "otwarty": ("PRZEJAZD WOLNY", "#4ade80"),
                "otwarty_stop": ("PRZEJAZD WOLNY — czeka", "#f2b544"),
                "czekanie": (f"ZAMKNIECIE ZA {self.odliczanie:.0f} s", "#f2b544"),
                "zamykanie": ("PODNOSZENIE SLUPKOW", "#f2b544"),
                "odmowa": ("DOSTEP ZABLOKOWANY", "#ff6b6b"),
                "cofa": ("DOSTEP ZABLOKOWANY", "#ff6b6b")}.get(self.faza,
                                                               ("GOTOWA", "#e8eef6"))
        self.create_oval(W - 330, 38, W - 320, 48, fill=stan[1], outline="")
        self.create_text(W - 308, 43, text=stan[0], anchor="w", fill=stan[1],
                         font=("Segoe UI Semibold", 11))
        if self.kto:
            self.create_text(W - 330, 72, text=self.kto, anchor="w", fill="#f2f6fb",
                             font=("Segoe UI", 11))
            self.create_text(W - 330, 96, text=self.tel, anchor="w", fill="#b9c6d6",
                             font=("Consolas", 10))
        if self.powod:
            self.create_text(W - 330, 96, text=self.powod, anchor="w", fill="#ff6b6b",
                             font=("Segoe UI", 9))

        for (x1, x2), opis in zip(PRZYCISKI_X, PRZYCISKI_OPIS):
            self.create_text((x1 + x2) / 2, H - 45, text=opis, fill="#f2f6fb",
                             font=("Segoe UI Semibold", 9))

    def klik_foto(self, zdarzenie):
        """Obsluga przyciskow wtopionych w zdjecie."""
        if not self.foto:
            return
        H = self.foto["_tlo"].size[1]
        if not (H - 64 <= zdarzenie.y <= H - 26):
            return
        for i, (x1, x2) in enumerate(PRZYCISKI_X):
            if x1 <= zdarzenie.x <= x2:
                if self.on_przycisk:
                    self.on_przycisk(i)
                return

    def rysuj_slupki(self, px, GY, p, mig):
        """Slupki blokujace chowane w jezdnie.

        Kolejnosc rysowania jest istotna: korpusy ida PRZED jezdnia, a jezdnia
        jest dorysowywana na nich. Dzieki temu slupek naprawde znika w gruncie,
        zamiast nachodzic na nawierzchnie w koncowej fazie chowania.
        """
        WYS = 116
        SZER = 26
        pozycje = [px - 108, px, px + 108]
        widoczne = WYS * (1.0 - p)
        pasm = 13
        W = max(self.winfo_width(), 900)

        def stal(t):
            j = max(0.0, 1.0 - abs(t - 0.34) / 0.66)
            if t < 0.34:
                return mix(SC["stal_lewa"], SC["stal2"], j ** 0.9)
            return mix(SC["stal1"], SC["stal2"], j ** 1.15)

        if mig:
            kol_led = "#f2b544"
        elif p > 0.9:
            kol_led = "#37c76a"
        else:
            kol_led = "#e5484d"

        # ---------- 1. korpusy (moga wystawac ponizej jezdni) ----------
        if widoczne > 1:
            for sx in pozycje:
                gora = GY - widoczne
                self._poswiata(sx, gora + 13, 17, kol_led, 5)
                for i in range(pasm):
                    t = i / (pasm - 1.0)
                    x1 = sx - SZER / 2 + t * SZER
                    x2 = sx - SZER / 2 + (t + 1.0 / (pasm - 1)) * SZER
                    self.create_rectangle(x1, gora + 6, x2 + 1, GY + 30,
                                          fill=stal(t), outline="")
                for yy in range(int(gora) + 22, int(GY) + 24, 13):
                    self.create_line(sx - SZER / 2 + 3, yy, sx + SZER / 2 - 3, yy,
                                     fill=SC["rysy"], width=1)
                yb = gora + 20
                for i in range(pasm):
                    t = i / (pasm - 1.0)
                    x1 = sx - SZER / 2 + t * SZER
                    x2 = sx - SZER / 2 + (t + 1.0 / (pasm - 1)) * SZER
                    j = max(0.0, 1.0 - abs(t - 0.34) / 0.66)
                    baza = "#d33c40" if 0.18 < t < 0.42 or 0.62 < t < 0.86 else "#f2f5f9"
                    self.create_rectangle(x1, yb, x2 + 1, yb + 9,
                                          fill=mix(baza, "#ffffff", j * 0.30), outline="")
                for dx in (-7, 0, 7):
                    self.create_rectangle(sx + dx - 2, gora + 10, sx + dx + 2, gora + 16,
                                          fill=kol_led, outline="")
                self.create_rectangle(sx - SZER / 2, gora + 2, sx + SZER / 2, gora + 9,
                                      fill=mix(SC["glowica"], "#000000", 0.15), outline="")
                self.create_oval(sx - SZER / 2, gora - 4, sx + SZER / 2, gora + 8,
                                 fill=SC["glowica"], outline=SC["krawedz"])
                self.create_oval(sx - SZER / 2 + 5, gora - 2, sx + SZER / 2 - 5, gora + 4,
                                 fill=SC["glowica2"], outline="")

        # ---------- 2. jezdnia NA korpusach — tu slupek wchodzi w grunt ----------
        self._gradient(0, GY, W, self.H, SC["jezdnia1"], SC["jezdnia2"], 12)
        self.create_line(0, GY, W, GY, fill=SC["krawedz"], width=2)
        for x in range(-30, W, 78):
            self.create_rectangle(x, GY + 46, x + 40, GY + 52,
                                  fill=SC["pasy"], outline="")

        # ---------- 3. cienie i plyty bazowe na wierzchu ----------
        for sx in pozycje:
            if widoczne > 4:
                self.create_oval(sx - SZER / 2 - 6, GY - 3,
                                 sx + SZER / 2 + 18 + widoczne * 0.40, GY + 9,
                                 fill=SC["cien"], outline="")
            self.create_oval(sx - SZER / 2 - 17, GY - 7, sx + SZER / 2 + 17, GY + 11,
                             fill=SC["plyta"], outline=SC["krawedz"])
            self.create_oval(sx - SZER / 2 - 12, GY - 5, sx + SZER / 2 + 12, GY + 8,
                             fill=SC["plyta2"], outline="")
            if widoczne <= 4:
                # pokrywa rowno z nawierzchnia — slupek calkowicie schowany
                self.create_oval(sx - SZER / 2 - 1, GY - 3, sx + SZER / 2 + 1, GY + 6,
                                 fill=mix(SC["plyta2"], SC["stal1"], 0.35),
                                 outline=SC["plyta"])
            else:
                # ciemna szczelina wokol korpusu wchodzacego w grunt
                self.create_oval(sx - SZER / 2 - 2, GY - 3, sx + SZER / 2 + 2, GY + 6,
                                 fill="#0d1117", outline="")
                for i in range(pasm):
                    t = i / (pasm - 1.0)
                    x1 = sx - SZER / 2 + t * SZER
                    x2 = sx - SZER / 2 + (t + 1.0 / (pasm - 1)) * SZER
                    self.create_rectangle(x1, GY - 2, x2 + 1, GY + 2,
                                          fill=mix(stal(t), "#000000", 0.45), outline="")

        # ---------- 4. znak zakazu ----------
        zx = px + 196
        self.create_line(zx, GY, zx, GY - 96, fill=SC["krawedz"], width=4)
        self.create_oval(zx - 20, GY - 130, zx + 20, GY - 90,
                         fill="#c9302f" if p < 0.5 else mix(SC["plyta"], "#000000", 0.2),
                         outline="#eef2f7", width=3)
        self.create_rectangle(zx - 13, GY - 114, zx + 13, GY - 106,
                              fill="#eef2f7", outline="")

    def rysuj_brame(self, px, GY, p, mig):
        """Brama przesuwna: skrzydlo odjezdza w bok wzdluz szyny."""
        SZER, WYS = 250, 104
        # szyna
        self.create_rectangle(px - 30, GY + 2, px + SZER + 40, GY + 8,
                              fill="#2b323b", outline="#3c444f")
        # slupy prowadzace
        for sx in (px - 18, px + SZER + 18):
            self._gradient(sx - 9, GY - WYS - 22, sx + 9, GY, "#39424e", "#232a33", 18)
            self.create_rectangle(sx - 9, GY - WYS - 22, sx + 9, GY, outline="#4c5764")
            self.create_rectangle(sx - 14, GY - 4, sx + 14, GY + 8,
                                  fill="#22272e", outline="")
        # lampa na slupie
        lx, ly = px - 18, GY - WYS - 32
        if mig:
            self._poswiata(lx, ly, 34, "#f0a93a", 7)
        self.create_oval(lx - 10, ly - 10, lx + 10, ly + 10,
                         fill="#f2b544" if mig else "#4a3a1c", outline="#5c6672", width=2)

        # cien skrzydla
        off = p * (SZER - 12)
        gx = px + off
        self.create_rectangle(gx + 6, GY + 6, gx + SZER + 6, GY + 14,
                              fill="#0e1218", outline="")
        # rama skrzydla
        self.create_rectangle(gx, GY - WYS, gx + SZER, GY - 6,
                              fill="#161d26", outline="#4d8fd6", width=2)
        # pionowe szczebliny
        for i in range(1, 13):
            bx = gx + i * (SZER / 13.0)
            self.create_line(bx, GY - WYS + 8, bx, GY - 14, fill="#3f7fc4", width=3)
        # poprzeczki
        for yy in (GY - WYS + 6, GY - 16):
            self.create_line(gx + 4, yy, gx + SZER - 4, yy, fill="#4d8fd6", width=3)
        # wozki jezdne
        for wx in (gx + 30, gx + SZER - 30):
            self.create_oval(wx - 7, GY - 8, wx + 7, GY + 6,
                             fill="#12161c", outline="#8b98a8", width=2)
        # pas odblaskowy
        for i in range(4):
            yy = GY - WYS + 18 + i * 18
            self.create_line(gx + SZER - 26, yy, gx + SZER - 8, yy,
                             fill="#f2b544" if i % 2 == 0 else "#d93b40", width=4)

    def rysuj_auto(self, x, GY):
        if x < -300 or x > 1600:
            return
        b = GY - 6
        # cien
        self.create_oval(x + 4, b - 6, x + 150, b + 10, fill="#0c1016", outline="")
        # nadwozie
        self.create_polygon(x + 26, b - 44, x + 48, b - 74, x + 104, b - 74,
                            x + 130, b - 44, fill="#1f4f8f", outline="", smooth=True)
        self._gradient(x + 6, b - 46, x + 148, b - 12, "#2c6fbf", "#173a6e", 14)
        self.create_rectangle(x + 6, b - 46, x + 148, b - 12, outline="#4d8fd6")
        # szyby
        self.create_polygon(x + 34, b - 46, x + 52, b - 70, x + 76, b - 70,
                            x + 76, b - 46, fill="#0e1a2b", outline="")
        self.create_polygon(x + 82, b - 46, x + 82, b - 70, x + 102, b - 70,
                            x + 124, b - 46, fill="#0e1a2b", outline="")
        # kola
        for wx in (x + 34, x + 116):
            self.create_oval(wx - 17, b - 20, wx + 17, b + 14,
                             fill="#12161c", outline="#39424e", width=3)
            self.create_oval(wx - 7, b - 10, wx + 7, b + 4,
                             fill="#59636f", outline="")
        # swiatla + stozek swiatla
        self.create_oval(x + 142, b - 36, x + 152, b - 28, fill="#fff3cd", outline="")
        self.create_polygon(x + 150, b - 36, x + 300, b - 52, x + 300, b - 8,
                            x + 150, b - 26, fill="#1a2230", outline="")
        self.create_oval(x - 2, b - 36, x + 8, b - 28, fill="#8f2a2a", outline="")

    def hud(self, W):
        typ = getattr(self, "vtyp_bramy", "slupki")
        if typ == "slupki":
            n_zamk = "SLUPKI PODNIESIONE — BLOKADA"
            n_otw = "SLUPKI OPUSZCZONE — PRZEJAZD"
            n_otwieranie, n_zamykanie = "OPUSZCZANIE SLUPKOW", "PODNOSZENIE SLUPKOW"
        elif typ == "przesuwna":
            n_zamk, n_otw = "BRAMA ZAMKNIETA", "BRAMA OTWARTA — PRZEJAZD"
            n_otwieranie, n_zamykanie = "OTWIERANIE", "ZAMYKANIE"
        else:
            n_zamk, n_otw = "SZLABAN ZAMKNIETY", "OTWARTY — PRZEJAZD"
            n_otwieranie, n_zamykanie = "OTWIERANIE", "ZAMYKANIE"

        stan = {"spoczynek": (n_zamk, DIM),
                "jedzie": ("POJAZD PODJEZDZA", DIM),
                "dzwoni": ("POLACZENIE PRZYCHODZACE", "#e8a33d"),
                "otwieranie": (n_otwieranie, OK),
                "otwarty": (n_otw, OK),
                "otwarty_stop": ("PRZEJAZD OTWARTY — czeka na zamkniecie", WARN),
                "czekanie": (f"AUTOZAMYKANIE ZA {self.odliczanie:.0f} s", WARN),
                "zamykanie": (n_zamykanie, WARN),
                "odmowa": ("DOSTEP ZABLOKOWANY", SC["alarm"]),
                "cofa": ("DOSTEP ZABLOKOWANY", SC["alarm"])}.get(self.faza, ("GOTOWY", DIM))
        # panel lewy
        self.create_rectangle(18, 18, 300, 88, fill=SC["tlo_hud"], outline=SC["ramka_hud"])
        self.create_text(34, 40, text="ZAPORA — WJAZD GLOWNY", anchor="w", fill=FG,
                         font=("Segoe UI Semibold", 12))
        self.create_text(34, 66, text=datetime.now().strftime("%d.%m.%Y   %H:%M:%S"),
                         anchor="w", fill=DIM, font=("Consolas", 10))
        # panel prawy - stan
        wys = 146 if self.powod else (118 if self.kto else 74)
        self.create_rectangle(W - 340, 18, W - 18, wys,
                              fill=SC["tlo_hud"], outline=SC["ramka_hud"])
        self.create_oval(W - 322, 38, W - 310, 50, fill=stan[1], outline="")
        self.create_text(W - 300, 44, text=stan[0], anchor="w", fill=stan[1],
                         font=("Segoe UI Semibold", 11))
        if self.kto:
            self.create_text(W - 322, 76, text=self.kto, anchor="w", fill=FG,
                             font=("Segoe UI", 11))
            self.create_text(W - 322, 98, text=self.tel, anchor="w", fill=DIM,
                             font=("Consolas", 10))
        if self.powod:
            self.create_text(W - 20, 132, text=self.powod, anchor="e",
                             fill=SC["alarm"], font=("Segoe UI", 9))
        # informacja o trybie przekaznika
        self.create_text(20, self.H - 22,
                         text=("przekaznik: impuls" if self.tryb == "impuls"
                               else "przekaznik: stan zalaczony")
                              + f"   ·   czas otwarcia {self.czas_otwarcia} s"
                              + ("   ·   autozamykanie" if self.autozamykanie
                                 else "   ·   BEZ autozamykania"),
                         anchor="w", fill=DIM, font=("Consolas", 9))
        # pasek postepu ramienia
        bw = 200
        self.create_rectangle(W - 340, self.H - 40, W - 340 + bw, self.H - 30,
                              fill=BG3, outline=SC["ramka_hud"])
        self.create_rectangle(W - 340, self.H - 40,
                              W - 340 + bw * self.postep, self.H - 30,
                              fill=ACC, outline="")
        self.create_text(W - 130, self.H - 35, text=f"{int(self.postep * 100)}%",
                         anchor="w", fill=DIM, font=("Consolas", 9))

    # ---------- animacja ----------
    def _petla(self):
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        self.krok()
        self.rysuj()
        self.after(24, self._petla)

    def krok(self):
        f = self.faza
        if f == "jedzie":
            self.auto_x += 6.5
            if self.auto_x >= 200:
                self.faza = "dzwoni"
                self.t = 0
                self.on_event(f"{self.kto} — polaczenie do modulu")
        elif f == "dzwoni":
            self.t += 1
            if self.t > 34:
                if getattr(self, "dozwolony", True):
                    self.faza = "otwieranie"
                    self.t = 0
                    self.on_event("numer rozpoznany — "
                                  + ("impuls na przekaznik" if self.tryb == "impuls"
                                     else "przekaznik zalaczony"))
                else:
                    self.faza = "odmowa"
                    self.t = 0
                    self.on_event("ODMOWA: " + self.powod)
        elif f == "otwieranie":
            self.t += 1
            kl = 78 if getattr(self, "vtyp_bramy", "slupki") == "slupki" else 55
            self.postep = ease(self.t / float(kl))
            if self.t >= kl:
                self.postep = 1.0
                self.faza = "otwarty"
                self.t = 0
        elif f == "odmowa":
            self.t += 1
            if self.t > 70:
                self.faza = "cofa"
        elif f == "cofa":
            self.auto_x -= 7.0
            if self.auto_x < -300:
                self.faza = "spoczynek"
                self.busy = False
                self.kto = self.tel = self.powod = ""
                self.auto_x = -260.0
        elif f == "otwarty":
            if self.busy:
                self.auto_x += 7.5
                if self.auto_x > 1500:
                    if self.autozamykanie:
                        self.faza = "czekanie"
                        self.t = 0
                        self.on_event(
                            f"przejazd zakonczony — autozamykanie za {self.czas_otwarcia} s")
                    else:
                        self.faza = "otwarty_stop"
                        self.busy = False
                        self.on_event("autozamykanie wylaczone — brama pozostaje otwarta")
        elif f == "czekanie":
            self.t += 1
            self.odliczanie = max(0.0, self.czas_otwarcia - self.t / 41.0)
            if self.odliczanie <= 0:
                self.faza = "zamykanie"
                self.t = 0
                self.on_event("zamykam")
        elif f == "zamykanie":
            self.t += 1
            kl = 84 if getattr(self, "vtyp_bramy", "slupki") == "slupki" else 60
            self.postep = 1.0 - ease(self.t / float(kl))
            if self.t >= kl:
                self.postep = 0.0
                self.faza = "spoczynek"
                self.busy = False
                self.auto_x = -260.0
                self.kto = self.tel = ""
                self.on_event("szlaban zamkniety")

    # ---------- API ----------
    def przejazd(self, imie, tel, dozwolony=True, powod=""):
        if self.busy:
            return
        self.busy = True
        self.kto, self.tel = imie, tel
        self.powod = "" if dozwolony else powod
        self.dozwolony = dozwolony
        self.auto_x = -260.0
        self.postep = 0.0
        self.t = 0
        self.odliczanie = 0.0
        self.faza = "jedzie"
        self.on_event(f"wjazd: {imie} {tel}")

    def parametry(self, m):
        """Przenosi ustawienia modulu do animacji."""
        self.czas_otwarcia = int(m.get("czas_otwarcia", 8))
        self.autozamykanie = bool(m.get("autozamykanie", True))
        self.opoznienie = int(m.get("opoznienie", 2))
        self.tryb = m.get("tryb", "impuls")

    def recznie(self, otwierac):
        if self.busy:
            return
        if otwierac and self.postep < 1.0:
            self.faza = "otwieranie"
            self.t = int(ease_inv(self.postep) * 55)
            self.on_event("reczne otwieranie")
        elif not otwierac and self.postep > 0.0:
            self.faza = "zamykanie"
            self.t = int((1 - ease_inv(self.postep)) * 60)
            self.on_event("reczne zamykanie")


def ease_inv(y):
    """Przyblizona odwrotnosc smoothstep (do wznowienia animacji od stanu posredniego)."""
    lo, hi = 0.0, 1.0
    for _ in range(24):
        mid = (lo + hi) / 2
        if ease(mid) < y:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# =============================== APLIKACJA ===============================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP} v{VER}")
        self.configure(bg=BG)
        # dopasowanie do rozdzielczosci — na laptopie 1366x768 okno musi byc mniejsze
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        if sh < 880:
            Scena.H, Scena.GY, Scena.ARM = 340, 274, 168
        self.geometry(f"{min(1180, sw - 60)}x{min(900, sh - 80)}")
        self.minsize(min(1000, sw - 40), min(700, sh - 60))

        # czcionki: rosna przy skalowaniu ekranu, ale z limitem zeby nic sie nie rozjechalo
        try:
            wsp = max(1.0, min(1.25, dpi_systemu() / 96.0))
            self.tk.call("tk", "scaling", 1.3333 * wsp)
        except Exception:
            pass

        self.d = wczytaj()
        self.foto_material = None
        ustaw_motyw(self.d.get("motyw", "ciemny"))
        self.configure(bg=BG)
        self.mod_idx = 0
        self.widok = "podglad"
        self.logo_img = None
        ico = zasob("ikona.ico")
        if ico:
            try:
                self.iconbitmap(ico)
            except Exception:
                pass
        self._styl()
        self._ui()
        self.protocol("WM_DELETE_WINDOW", self.koniec)
        self.withdraw()
        self.after(60, self.ekran_logowania)

    def _styl(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=BG2)
        s.configure("TLabel", background=BG, foreground=FG)
        s.configure("Card.TLabel", background=BG2, foreground=FG)
        s.configure("Dim.TLabel", background=BG, foreground=DIM)
        s.configure("H1.TLabel", background=BG, foreground=FG,
                    font=("Segoe UI Semibold", 16))
        s.configure("Big.TLabel", background=BG2, foreground=ACC,
                    font=("Segoe UI Semibold", 21))
        s.configure("TEntry", fieldbackground=BG3, foreground=FG, insertcolor=FG,
                    bordercolor=BG3, lightcolor=BG3, darkcolor=BG3)
        s.configure("TCombobox", fieldbackground=BG3, background=BG3, foreground=FG)
        s.configure("TButton", background=BG3, foreground=FG, borderwidth=0,
                    padding=(14, 8), font=("Segoe UI", 10))
        s.map("TButton", background=[("active", "#2c3846")])
        s.configure("Acc.TButton", background=ACC, foreground="#fff")
        s.map("Acc.TButton", background=[("active", "#5aa4ff")])
        s.configure("Ok.TButton", background=OK, foreground="#06210f")
        s.map("Ok.TButton", background=[("active", "#4ce07f")])
        s.configure("Treeview", background=BG2, fieldbackground=BG2, foreground=FG,
                    borderwidth=0, rowheight=29)
        s.configure("Treeview.Heading", background=BG3, foreground=DIM,
                    borderwidth=0, font=("Segoe UI", 9))
        s.map("Treeview", background=[("selected", ACC)], foreground=[("selected", "#fff")])

    # ---------------- szkielet ----------------
    def _ui(self):
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=20, pady=(12, 8))

        # --- logo ---
        lg = zasob("logo.png")
        if lg:
            try:
                self.logo_img = tk.PhotoImage(file=lg)
                while self.logo_img.height() > 54:
                    self.logo_img = self.logo_img.subsample(2, 2)
                tk.Label(head, image=self.logo_img, bg=BG).pack(side="left", padx=(0, 12))
            except Exception:
                self.logo_img = None
        if not self.logo_img:
            emb = tk.Canvas(head, width=46, height=46, bg=BG, highlightthickness=0)
            emb.pack(side="left", padx=(0, 12))
            self.emblemat(emb, 46)

        tyt = tk.Frame(head, bg=BG)
        tyt.pack(side="left", padx=(0, 28))
        tk.Label(tyt, text=self.d["marka"]["nazwa"], bg=BG, fg=FG,
                 font=("Segoe UI Semibold", 15)).pack(anchor="w")
        tk.Label(tyt, text=self.d["marka"]["podtytul"], bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w")

        self.tabs = {}
        for k, t in [("podglad", "PODGLAD"), ("moduly", "MODULY I KARTY SIM"),
                     ("sterownik", "STEROWNIK"), ("historia", "HISTORIA I RAPORTY")]:
            b = tk.Label(head, text=t, bg=BG, fg=DIM, font=("Segoe UI Semibold", 10),
                         padx=18, pady=8, cursor="hand2")
            b.pack(side="left", padx=(0, 6))
            b.bind("<Button-1>", lambda e, kk=k: self.przelacz(kk))
            self.tabs[k] = b

        prawy = tk.Frame(head, bg=BG)
        prawy.pack(side="right")
        for txt, cmd in [(self._etykieta_motywu(), self.przelacz_motyw),
                         ("?  Instrukcja", self.okno_instrukcja),
                         ("O programie", self.okno_o_programie),
                         ("Zmien PIN", self.okno_pin),
                         ("Zablokuj", self.zablokuj)]:
            tk.Label(prawy, text=txt, bg=BG3, fg=DIM, font=("Segoe UI", 9),
                     padx=12, pady=7, cursor="hand2").pack(side="left", padx=(6, 0))
            prawy.winfo_children()[-1].bind("<Button-1>", lambda e, c=cmd: c())

        self.kontener = tk.Frame(self, bg=BG)
        self.kontener.pack(fill="both", expand=True)

        self.f_podglad = tk.Frame(self.kontener, bg=BG)
        self.f_moduly = tk.Frame(self.kontener, bg=BG)
        self.f_sterownik = tk.Frame(self.kontener, bg=BG)
        self.f_historia = tk.Frame(self.kontener, bg=BG)
        self._buduj_podglad()
        self._buduj_moduly()
        self._buduj_sterownik()
        self._buduj_historie()
        self.przelacz("podglad")

    def przelacz(self, k):
        self.widok = k
        for kk, b in self.tabs.items():
            b.config(fg=FG if kk == k else DIM, bg=BG3 if kk == k else BG)
        for f in (self.f_podglad, self.f_moduly, self.f_sterownik, self.f_historia):
            f.pack_forget()
        if k == "podglad":
            self.odswiez()
            self.f_podglad.pack(fill="both", expand=True)
        elif k == "moduly":
            self.odswiez_moduly()
            self.f_moduly.pack(fill="both", expand=True)
        elif k == "sterownik":
            self.odswiez_sterownik()
            self.f_sterownik.pack(fill="both", expand=True)
        else:
            self.odswiez_historie()
            self.f_historia.pack(fill="both", expand=True)

    # ---------------- WIDOK: PODGLAD ----------------
    def _buduj_podglad(self):
        f = self.f_podglad
        wyb = tk.Frame(f, bg=BG)
        wyb.pack(fill="x", padx=20, pady=(0, 8))
        tk.Label(wyb, text="Obiekt:", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 8))
        self.v_modul = tk.StringVar()
        self.cb_modul = ttk.Combobox(wyb, textvariable=self.v_modul, state="readonly",
                                     width=42)
        self.cb_modul.pack(side="left")
        self.cb_modul.bind("<<ComboboxSelected>>", self.zmien_modul)
        self.lbl_sim = tk.Label(wyb, text="", bg=BG, fg=DIM,
                                font=("Consolas", 9))
        self.lbl_sim.pack(side="left", padx=14)

        self.scena = Scena(f, on_event=self.zdarzenie)
        self.scena.pack(fill="x", padx=20)

        ster = tk.Frame(f, bg=BG)
        ster.pack(fill="x", padx=20, pady=(14, 6))
        ttk.Button(ster, text="▶  SYMULUJ PRZEJAZD", style="Ok.TButton",
                   command=self.przejazd).pack(side="left")
        ttk.Button(ster, text="Otworz",
                   command=lambda: self.reczne(True)).pack(side="left", padx=(12, 6))
        ttk.Button(ster, text="Zamknij",
                   command=lambda: self.reczne(False)).pack(side="left")
        self.lbl_ostatni = tk.Label(ster, text="", bg=BG, fg=DIM, font=("Segoe UI", 9))
        self.lbl_ostatni.pack(side="right")

        dol = tk.Frame(f, bg=BG)
        dol.pack(fill="both", expand=True, padx=20, pady=(6, 16))

        lewa = tk.Frame(dol, bg=BG)
        lewa.pack(side="left", fill="both", expand=True)
        tk.Label(lewa, text="Numery uprawnione", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))
        cols = ("imie", "tel", "harm", "stan", "ile", "ostatnio")
        self.tv = ttk.Treeview(lewa, columns=cols, show="headings", height=7)
        for c, t, w, a in [("imie", "KIEROWCA", 175, "w"), ("tel", "TELEFON", 125, "w"),
                           ("harm", "HARMONOGRAM", 175, "w"), ("stan", "STAN", 95, "center"),
                           ("ile", "WJAZDOW", 75, "center"),
                           ("ostatnio", "OSTATNIO", 120, "w")]:
            self.tv.heading(c, text=t)
            self.tv.column(c, width=w, anchor=a)
        self.tv.tag_configure("blok", foreground="#d6444a")
        self.tv.tag_configure("ogr", foreground=WARN)
        self.tv.pack(fill="both", expand=True)
        self.tv.bind("<Double-1>", lambda e: self.edytuj())

        b = tk.Frame(lewa, bg=BG)
        b.pack(fill="x", pady=(10, 0))
        ttk.Button(b, text="+  Dodaj", style="Acc.TButton",
                   command=self.dodaj).pack(side="left")
        ttk.Button(b, text="Edytuj", command=self.edytuj).pack(side="left", padx=8)
        ttk.Button(b, text="Usun", command=self.usun).pack(side="left")
        ttk.Button(b, text="Wpusc zaznaczonego", style="Ok.TButton",
                   command=self.przejazd).pack(side="right")

        prawa = tk.Frame(dol, bg=BG, width=330)
        prawa.pack(side="left", fill="y", padx=(20, 0))
        prawa.pack_propagate(False)
        tk.Label(prawa, text="Zdarzenia (biezaca sesja)", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))
        self.lb = tk.Listbox(prawa, bg=BG2, fg=FG, borderwidth=0, highlightthickness=0,
                             font=("Consolas", 9), selectbackground=ACC)
        self.lb.pack(fill="both", expand=True)
        self.odswiez()

    # ---------------- WIDOK: HISTORIA ----------------
    def _buduj_historie(self):
        f = self.f_historia
        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", padx=20, pady=(6, 12))
        tk.Label(top, text="Historia otwarc", bg=BG, fg=FG,
                 font=("Segoe UI Semibold", 15)).pack(anchor="w")
        tk.Label(top, text="Kto i kiedy otwieral brame. Zapisywane trwale na dysku.",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        # kafelki statystyk
        kaf = tk.Frame(f, bg=BG)
        kaf.pack(fill="x", padx=20)
        self.kafle = {}
        for key, tytul in [("dzis", "DZISIAJ"), ("tydzien", "OSTATNIE 7 DNI"),
                           ("miesiac", "TEN MIESIAC"), ("razem", "LACZNIE"),
                           ("top", "NAJCZESCIEJ")]:
            c = tk.Frame(kaf, bg=BG2)
            c.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Label(c, text=tytul, bg=BG2, fg=DIM,
                     font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(14, 0))
            l = tk.Label(c, text="—", bg=BG2, fg=ACC, font=("Segoe UI Semibold", 19),
                         anchor="w", wraplength=190, justify="left")
            l.pack(anchor="w", padx=16, pady=(2, 14))
            self.kafle[key] = l

        # filtry
        fl = tk.Frame(f, bg=BG)
        fl.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(fl, text="Kierowca", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        self.f_osoba = tk.StringVar(value="— wszyscy —")
        self.cb_osoba = ttk.Combobox(fl, textvariable=self.f_osoba, state="readonly",
                                     width=26, values=["— wszyscy —"])
        self.cb_osoba.pack(side="left")
        self.cb_osoba.bind("<<ComboboxSelected>>", lambda e: self.odswiez_historie())

        tk.Label(fl, text="  Od", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(side="left", padx=(16, 6))
        self.f_od = tk.StringVar(value="")
        e1 = ttk.Entry(fl, textvariable=self.f_od, width=12)
        e1.pack(side="left")
        tk.Label(fl, text="Do", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(side="left", padx=(10, 6))
        self.f_do = tk.StringVar(value="")
        e2 = ttk.Entry(fl, textvariable=self.f_do, width=12)
        e2.pack(side="left")
        tk.Label(fl, text="(RRRR-MM-DD)", bg=BG, fg=DIM,
                 font=("Segoe UI", 8)).pack(side="left", padx=(8, 0))
        for e in (e1, e2):
            e.bind("<Return>", lambda ev: self.odswiez_historie())
        ttk.Button(fl, text="Filtruj", command=self.odswiez_historie).pack(side="left", padx=12)
        ttk.Button(fl, text="Wyczysc filtry", command=self.reset_filtry).pack(side="left")

        # tabela
        tw = tk.Frame(f, bg=BG)
        tw.pack(fill="both", expand=True, padx=20)
        cols = ("lp", "data", "godz", "imie", "tel", "tryb")
        self.tvh = ttk.Treeview(tw, columns=cols, show="headings")
        for c, t, w, a in [("lp", "LP", 55, "center"), ("data", "DATA", 120, "w"),
                           ("godz", "GODZINA", 100, "w"), ("imie", "KIEROWCA", 260, "w"),
                           ("tel", "TELEFON", 150, "w"), ("tryb", "SPOSOB", 170, "w")]:
            self.tvh.heading(c, text=t)
            self.tvh.column(c, width=w, anchor=a)
        sb = ttk.Scrollbar(tw, orient="vertical", command=self.tvh.yview)
        self.tvh.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tvh.pack(fill="both", expand=True)
        self.tvh.tag_configure("reczne", foreground=WARN)

        bar = tk.Frame(f, bg=BG)
        bar.pack(fill="x", padx=20, pady=14)
        ttk.Button(bar, text="Raport do wydruku", style="Acc.TButton",
                   command=self.raport_html).pack(side="left")
        ttk.Button(bar, text="Eksport CSV", command=self.eksport_csv).pack(side="left", padx=10)
        self.lbl_ile = tk.Label(bar, text="", bg=BG, fg=DIM, font=("Segoe UI", 9))
        self.lbl_ile.pack(side="left", padx=14)
        ttk.Button(bar, text="Wyczysc historie",
                   command=self.czysc_historie).pack(side="right")

    # ---------------- historia: logika ----------------
    def zapisz_wjazd(self, imie, tel, tryb):
        self.d.setdefault("historia", []).append({
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "imie": imie, "tel": tel, "tryb": tryb})
        zapisz(self.d)
        self.odswiez()

    def _filtruj(self):
        h = list(self.d.get("historia", []))
        osoba = self.f_osoba.get()
        if osoba and not osoba.startswith("—"):
            h = [x for x in h if x.get("imie") == osoba]
        od, do = self.f_od.get().strip(), self.f_do.get().strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", od):
            h = [x for x in h if x.get("ts", "")[:10] >= od]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", do):
            h = [x for x in h if x.get("ts", "")[:10] <= do]
        h.sort(key=lambda x: x.get("ts", ""), reverse=True)
        return h

    def reset_filtry(self):
        self.f_osoba.set("— wszyscy —")
        self.f_od.set("")
        self.f_do.set("")
        self.odswiez_historie()

    def odswiez_historie(self):
        cala = self.d.get("historia", [])
        osoby = sorted({x.get("imie", "") for x in cala if x.get("imie")})
        self.cb_osoba.configure(values=["— wszyscy —"] + osoby)

        h = self._filtruj()
        for i in self.tvh.get_children():
            self.tvh.delete(i)
        for i, x in enumerate(h, 1):
            ts = x.get("ts", "")
            self.tvh.insert("", "end", tags=("reczne",) if "eczn" in x.get("tryb", "") else (),
                            values=(i, ts[:10], ts[11:19], x.get("imie", ""),
                                    x.get("tel", ""), x.get("tryb", "")))
        self.lbl_ile.config(text=f"pozycji po filtrze: {len(h)}   /   w bazie: {len(cala)}")

        dzis = datetime.now().strftime("%Y-%m-%d")
        m = datetime.now().strftime("%Y-%m")
        t7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        licz = {}
        for x in cala:
            licz[x.get("imie", "?")] = licz.get(x.get("imie", "?"), 0) + 1
        top = max(licz.items(), key=lambda kv: kv[1])[0] if licz else "—"
        self.kafle["dzis"].config(text=str(sum(1 for x in cala if x.get("ts", "")[:10] == dzis)))
        self.kafle["tydzien"].config(text=str(sum(1 for x in cala if x.get("ts", "")[:10] >= t7)))
        self.kafle["miesiac"].config(text=str(sum(1 for x in cala if x.get("ts", "")[:7] == m)))
        self.kafle["razem"].config(text=str(len(cala)))
        self.kafle["top"].config(text=top, font=("Segoe UI Semibold", 12))

    def czysc_historie(self):
        n = len(self.d.get("historia", []))
        if not n:
            return
        if messagebox.askyesno("Potwierdz",
                               f"Skasowac cala historie ({n} pozycji)?\n"
                               "Tej operacji nie da sie cofnac."):
            self.d["historia"] = []
            zapisz(self.d)
            self.odswiez_historie()
            self.odswiez()

    def eksport_csv(self):
        h = self._filtruj()
        if not h:
            messagebox.showinfo("Pusto", "Brak danych do eksportu.")
            return
        p = filedialog.asksaveasfilename(defaultextension=".csv",
                                         initialfile="historia-otwarc.csv",
                                         filetypes=[("Plik CSV", "*.csv")])
        if not p:
            return
        try:
            with open(p, "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.writer(fh, delimiter=";")
                w.writerow(["Data", "Godzina", "Kierowca", "Telefon", "Sposob"])
                for x in h:
                    ts = x.get("ts", "")
                    w.writerow([ts[:10], ts[11:19], x.get("imie", ""),
                                x.get("tel", ""), x.get("tryb", "")])
            messagebox.showinfo("Gotowe", f"Zapisano {len(h)} pozycji.")
        except Exception as e:
            messagebox.showerror("Blad", str(e))

    def raport_html(self):
        h = self._filtruj()
        if not h:
            messagebox.showinfo("Pusto", "Brak danych do raportu.")
            return
        licz = {}
        godz = {}
        for x in h:
            licz[x.get("imie", "?")] = licz.get(x.get("imie", "?"), 0) + 1
            g = x.get("ts", "")[11:13]
            if g:
                godz[g] = godz.get(g, 0) + 1
        rank = sorted(licz.items(), key=lambda kv: -kv[1])
        szczyt = max(godz.items(), key=lambda kv: kv[1])[0] + ":00" if godz else "—"
        zakres = f"{h[-1].get('ts', '')[:10]} — {h[0].get('ts', '')[:10]}"
        maxv = rank[0][1] if rank else 1

        wiersze = "".join(
            f"<tr><td>{i}</td><td>{x.get('ts','')[:10]}</td><td>{x.get('ts','')[11:19]}</td>"
            f"<td>{x.get('imie','')}</td><td>{x.get('tel','')}</td>"
            f"<td>{x.get('tryb','')}</td></tr>"
            for i, x in enumerate(h, 1))
        slupki = "".join(
            f"<tr><td>{n}</td><td class='r'>{v}</td>"
            f"<td class='bw'><span class='bar' style='width:{int(v / maxv * 100)}%'></span></td></tr>"
            for n, v in rank)

        html = f"""<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">
<title>Raport otwarc bramy</title><style>
*{{box-sizing:border-box}}
body{{font-family:Segoe UI,Arial,sans-serif;margin:0;padding:38px;color:#1c2430;background:#fff}}
h1{{margin:0 0 4px;font-size:24px}}
.sub{{color:#6b7684;font-size:13px;margin-bottom:26px}}
.kafle{{display:flex;gap:14px;margin-bottom:26px;flex-wrap:wrap}}
.k{{flex:1;min-width:130px;border:1px solid #dde3ea;border-radius:9px;padding:14px 16px}}
.k b{{display:block;font-size:10px;letter-spacing:.6px;color:#7a8595;font-weight:600}}
.k span{{font-size:24px;font-weight:700;color:#1f5fa8}}
h2{{font-size:15px;margin:26px 0 10px;padding-bottom:7px;border-bottom:2px solid #1f5fa8}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}}
th{{text-align:left;background:#f2f5f9;padding:8px 10px;font-size:10px;
letter-spacing:.5px;color:#5d6875;border-bottom:1px solid #dde3ea}}
td{{padding:7px 10px;border-bottom:1px solid #eef1f5}}
tr:nth-child(even) td{{background:#fafbfd}}
.r{{text-align:right;font-weight:600;width:60px}}
.bw{{width:45%}}
.bar{{display:block;height:9px;border-radius:5px;background:#1f5fa8}}
.stopka{{margin-top:34px;padding-top:14px;border-top:1px solid #dde3ea;
color:#8b95a3;font-size:11px;display:flex;justify-content:space-between}}
@media print{{body{{padding:14px}} .k{{border-color:#bbb}}}}
</style></head><body>
<h1>Raport otwarc bramy</h1>
<div class="sub">{self.d["marka"]["nazwa"]} &nbsp;·&nbsp; wygenerowano {datetime.now():%d.%m.%Y %H:%M}
&nbsp;·&nbsp; zakres danych: {zakres}</div>
<div class="kafle">
<div class="k"><b>OTWARC LACZNIE</b><span>{len(h)}</span></div>
<div class="k"><b>UPRAWNIONYCH OSOB</b><span>{len(rank)}</span></div>
<div class="k"><b>SZCZYT RUCHU</b><span>{szczyt}</span></div>
<div class="k"><b>NAJCZESCIEJ</b><span style="font-size:15px">{rank[0][0] if rank else '—'}</span></div>
</div>
<h2>Ranking wjazdow</h2>
<table><tr><th>KIEROWCA</th><th class="r">WJAZDOW</th><th>UDZIAL</th></tr>{slupki}</table>
<h2>Pelna lista zdarzen</h2>
<table><tr><th>LP</th><th>DATA</th><th>GODZINA</th><th>KIEROWCA</th>
<th>TELEFON</th><th>SPOSOB</th></tr>{wiersze}</table>
<div class="stopka"><span>Akademia Wychowania Fizycznego w Warszawie — kontrola wjazdu</span>
<span>{APP} v{VER}</span></div>
</body></html>"""
        p = os.path.join(kat_dir(), "raport.html")
        try:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(html)
            webbrowser.open("file:///" + p.replace("\\", "/"))
            self.zdarzenie("wygenerowano raport")
        except Exception as e:
            messagebox.showerror("Blad", str(e))

    # ---------------- lista numerow ----------------
    def modul(self):
        if not self.d["moduly"]:
            self.d["moduly"] = [nowy_modul()]
        self.mod_idx = max(0, min(self.mod_idx, len(self.d["moduly"]) - 1))
        return self.d["moduly"][self.mod_idx]

    def zmien_modul(self, e=None):
        for i, m in enumerate(self.d["moduly"]):
            if m["nazwa"] == self.v_modul.get():
                self.mod_idx = i
                break
        self.scena.parametry(self.modul())
        self.odswiez()

    def _stat_osoby(self, imie):
        wpisy = [x for x in self.d.get("historia", [])
                 if x.get("imie") == imie and x.get("tryb", "").startswith("przejazd")]
        if not wpisy:
            return 0, "—"
        ost = max(x.get("ts", "") for x in wpisy)
        return len(wpisy), f"{ost[8:10]}.{ost[5:7]} {ost[11:16]}"

    def _opis_harm(self, n):
        dni = n.get("dni") or list(DNI)
        od, do = n.get("godz_od", "00:00"), n.get("godz_do", "23:59")
        if len(dni) == 7 and od == "00:00" and do == "23:59":
            opis = "caly czas"
        else:
            if dni == ["pn", "wt", "sr", "cz", "pt"]:
                d = "pn-pt"
            elif len(dni) == 7:
                d = "codziennie"
            else:
                d = ",".join(dni)
            opis = f"{d}  {od}-{do}"
        wd = (n.get("wazny_do") or "").strip()
        if wd:
            opis += f"  do {wd}"
        return opis

    def odswiez(self):
        if not hasattr(self, "tv"):
            return
        nazwy = [m["nazwa"] for m in self.d["moduly"]]
        self.cb_modul.configure(values=nazwy)
        m = self.modul()
        self.v_modul.set(m["nazwa"])
        self.lbl_sim.config(text=f"SIM modulu: {m.get('sim') or '(nie podano)'}"
                                 f"   ·   {m.get('typ', '')}")
        self.scena.parametry(m)
        self.scena.vtyp_bramy = m.get("wyglad", "slupki")
        self.scena.nazwa_obiektu = m["nazwa"].upper()
        self.scena.on_przycisk = self.przycisk_sceny
        if m.get("zdjecie", True):
            if self.foto_material is None:
                self.foto_material = wczytaj_foto()
            self.scena.foto = self.foto_material
        else:
            self.scena.foto = None

        for i in self.tv.get_children():
            self.tv.delete(i)
        for i, n in enumerate(m.get("numery", [])):
            ile, ost = self._stat_osoby(n.get("imie", ""))
            ok, powod = sprawdz_dostep(n, modul=m)
            if not n.get("aktywny", True):
                stan, tag = "ZABLOKOWANY", "blok"
            elif ok:
                stan, tag = "wpuszcza", ""
            else:
                stan, tag = "poza godz.", "ogr"
            self.tv.insert("", "end", iid=str(i), tags=(tag,) if tag else (),
                           values=(n.get("imie", ""), n.get("tel", ""),
                                   self._opis_harm(n), stan, ile, ost))
        h = self.d.get("historia", [])
        if h and hasattr(self, "lbl_ostatni"):
            o = max(h, key=lambda x: x.get("ts", ""))
            self.lbl_ostatni.config(
                text=f"ostatnie zdarzenie:  {o.get('imie', '')}  ·  "
                     f"{o.get('ts', '')[8:10]}.{o.get('ts', '')[5:7]} {o.get('ts', '')[11:16]}")

    def _sel(self):
        s = self.tv.selection()
        return int(s[0]) if s else None

    def dodaj(self):
        self.dialog(None)

    def edytuj(self):
        i = self._sel()
        if i is None:
            self.zdarzenie("zaznacz pozycje")
            return
        self.dialog(i)

    def usun(self):
        i = self._sel()
        if i is None:
            return
        n = self.modul()["numery"][i]
        if messagebox.askyesno("Potwierdz",
                               f"Usunac {n.get('imie')} ({n.get('tel')})?\n\n"
                               "Historia jego wjazdow zostanie zachowana."):
            del self.modul()["numery"][i]
            zapisz(self.d)
            self.odswiez()
            self.zdarzenie(f"usunieto: {n.get('imie')}")

    def dialog(self, idx):
        m = self.modul()
        lst = m.setdefault("numery", [])
        n = lst[idx] if idx is not None else {"imie": "", "tel": "", "uwagi": "",
                                              "aktywny": True, "dni": list(DNI),
                                              "godz_od": "00:00", "godz_do": "23:59",
                                              "wazny_do": ""}
        w = tk.Toplevel(self)
        w.title("Numer uprawniony")
        w.configure(bg=BG2)
        w.geometry("470x560")
        w.transient(self)
        w.grab_set()
        w.resizable(False, False)
        tk.Label(w, text="Numer uprawniony", bg=BG2, fg=FG,
                 font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=24, pady=(18, 2))
        tk.Label(w, text=f"obiekt: {m['nazwa']}", bg=BG2, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=24)

        pola = {}
        for k, lab in [("imie", "Kierowca / opis"), ("tel", "Numer telefonu"),
                       ("uwagi", "Uwagi")]:
            tk.Label(w, text=lab, bg=BG2, fg=DIM,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(10, 3))
            v = tk.StringVar(value=n.get(k, ""))
            ttk.Entry(w, textvariable=v).pack(fill="x", padx=24, ipady=4)
            pola[k] = v

        # --- harmonogram ---
        tk.Label(w, text="HARMONOGRAM DOSTEPU", bg=BG2, fg=ACC,
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=24, pady=(18, 6))
        dni_ram = tk.Frame(w, bg=BG2)
        dni_ram.pack(anchor="w", padx=22)
        vdni = {}
        for d in DNI:
            v = tk.BooleanVar(value=d in (n.get("dni") or DNI))
            tk.Checkbutton(dni_ram, text=d, variable=v, bg=BG2, fg=FG, selectcolor=BG3,
                           activebackground=BG2, activeforeground=FG,
                           font=("Segoe UI", 9)).pack(side="left", padx=1)
            vdni[d] = v

        godz = tk.Frame(w, bg=BG2)
        godz.pack(anchor="w", padx=24, pady=(10, 0))
        tk.Label(godz, text="od", bg=BG2, fg=DIM, font=("Segoe UI", 9)).pack(side="left")
        v_od = tk.StringVar(value=n.get("godz_od", "00:00"))
        ttk.Entry(godz, textvariable=v_od, width=7).pack(side="left", padx=(6, 14))
        tk.Label(godz, text="do", bg=BG2, fg=DIM, font=("Segoe UI", 9)).pack(side="left")
        v_do = tk.StringVar(value=n.get("godz_do", "23:59"))
        ttk.Entry(godz, textvariable=v_do, width=7).pack(side="left", padx=(6, 14))
        tk.Label(godz, text="wazny do", bg=BG2, fg=DIM,
                 font=("Segoe UI", 9)).pack(side="left")
        v_wd = tk.StringVar(value=n.get("wazny_do", ""))
        ttk.Entry(godz, textvariable=v_wd, width=12).pack(side="left", padx=6)

        tk.Label(w, text="godziny GG:MM,  data RRRR-MM-DD (puste = bezterminowo)",
                 bg=BG2, fg=DIM, font=("Segoe UI", 8)).pack(anchor="w",
                                                                  padx=24, pady=(6, 0))
        v_akt = tk.BooleanVar(value=n.get("aktywny", True))
        tk.Checkbutton(w, text="Numer aktywny (odznacz aby zablokowac wjazd)",
                       variable=v_akt, bg=BG2, fg=FG, selectcolor=BG3,
                       activebackground=BG2, activeforeground=FG,
                       font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(12, 0))

        def ok():
            tel = norm_tel(pola["tel"].get())
            if not pola["imie"].get().strip():
                messagebox.showwarning("Brak danych", "Podaj imie / opis.")
                return
            if len(re.sub(r"\D", "", tel)) < 9:
                messagebox.showwarning("Numer", "Niepoprawny numer telefonu.")
                return
            for v, nazwa in ((v_od.get(), "godzina od"), (v_do.get(), "godzina do")):
                if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", v.strip()):
                    messagebox.showwarning("Godzina",
                                           f"Niepoprawna {nazwa} — format GG:MM, np. 06:30.")
                    return
            wd = v_wd.get().strip()
            if wd and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", wd):
                messagebox.showwarning("Data", "Data w formacie RRRR-MM-DD, np. 2026-12-31.")
                return
            wybrane = [d for d in DNI if vdni[d].get()]
            if not wybrane:
                messagebox.showwarning("Harmonogram", "Zaznacz co najmniej jeden dzien.")
                return
            n.update({"imie": pola["imie"].get().strip(), "tel": tel,
                      "uwagi": pola["uwagi"].get().strip(), "dni": wybrane,
                      "godz_od": v_od.get().strip(), "godz_do": v_do.get().strip(),
                      "wazny_do": wd, "aktywny": v_akt.get()})
            if idx is None:
                lst.append(n)
                self.zdarzenie(f"dodano: {n['imie']}")
            else:
                self.zdarzenie(f"zapisano: {n['imie']}")
            zapisz(self.d)
            self.odswiez()
            w.destroy()

        bf = tk.Frame(w, bg=BG2)
        bf.pack(fill="x", padx=24, pady=18, side="bottom")
        ttk.Button(bf, text="Zapisz", style="Acc.TButton", command=ok).pack(side="right")
        ttk.Button(bf, text="Anuluj", command=w.destroy).pack(side="right", padx=8)
        w.bind("<Escape>", lambda e: w.destroy())

    # ---------------- akcje ----------------
    def przejazd(self):
        if self.scena.busy:
            return
        m = self.modul()
        lst = m.get("numery", [])
        if not lst:
            self.zdarzenie("brak numerow na liscie")
            return
        i = self._sel()
        if i is None:
            i = 0
            self.tv.selection_set("0")
        n = lst[i]
        ok, powod = sprawdz_dostep(n, modul=m)
        self.scena.parametry(m)
        self.scena.przejazd(n.get("imie", "?"), n.get("tel", ""), ok, powod)
        self.zapisz_wjazd(n.get("imie", "?"), n.get("tel", ""),
                          "przejazd (telefon)" if ok else f"ODMOWA — {powod}")

    def przycisk_sceny(self, nr):
        """Klikniecie przycisku wtopionego w zdjecie."""
        if nr == 0:
            self.przejazd()
        elif nr == 1:
            self.reczne(True)
        else:
            self.reczne(False)

    def reczne(self, otwierac):
        if self.scena.busy:
            return
        self.scena.parametry(self.modul())
        self.scena.recznie(otwierac)
        if otwierac:
            self.zapisz_wjazd("Obsluga", "—", "reczne otwarcie")

    def zdarzenie(self, txt):
        self.lb.insert(0, f"{datetime.now():%H:%M:%S}  {txt}")
        if self.lb.size() > 300:
            self.lb.delete(300, "end")

    # ---------------- WIDOK: MODULY I KARTY SIM ----------------
    def _buduj_moduly(self):
        f = self.f_moduly
        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", padx=20, pady=(6, 12))
        tk.Label(top, text="Moduly GSM i karty SIM", bg=BG, fg=FG,
                 font=("Segoe UI Semibold", 15)).pack(anchor="w")
        tk.Label(top, text="Kazdy modul to jedna brama. Ustawienia sterowania "
                           "dzialaja juz teraz w symulacji.",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        pas = tk.Frame(f, bg=mix(BG2, WARN, 0.16))
        pas.pack(fill="x", padx=20, pady=(0, 12))
        tk.Label(pas, text="  TRYB DEMO — moduly nie sa jeszcze polaczone przez internet. "
                           "Ustawienia sa zapisywane i beda wyslane do sprzetu po podlaczeniu.",
                 bg=mix(BG2, WARN, 0.16), fg=WARN, font=("Segoe UI", 9),
                 anchor="w", pady=9).pack(fill="x")

        srodek = tk.Frame(f, bg=BG)
        srodek.pack(fill="both", expand=True, padx=20)

        lewa = tk.Frame(srodek, bg=BG)
        lewa.pack(side="left", fill="both", expand=True)
        cols = ("nazwa", "sim", "typ", "ster", "praca", "czas", "ile", "stan")
        self.tvm = ttk.Treeview(lewa, columns=cols, show="headings", height=9)
        for c, t, w, a in [("nazwa", "OBIEKT", 165, "w"), ("sim", "KARTA SIM", 125, "w"),
                           ("typ", "TYP MODULU", 145, "w"),
                           ("ster", "STEROWANIE", 95, "center"),
                           ("praca", "TRYB PRACY", 95, "center"),
                           ("czas", "CZAS OTW.", 85, "center"),
                           ("ile", "NUMEROW", 80, "center"),
                           ("stan", "POLACZENIE", 95, "center")]:
            self.tvm.heading(c, text=t)
            self.tvm.column(c, width=w, anchor=a)
        self.tvm.tag_configure("demo", foreground=WARN)
        self.tvm.pack(fill="both", expand=True)
        self.tvm.bind("<Double-1>", lambda e: self.edytuj_modul())

        b = tk.Frame(lewa, bg=BG)
        b.pack(fill="x", pady=(12, 0))
        ttk.Button(b, text="+  Dodaj modul", style="Acc.TButton",
                   command=lambda: self.dialog_modul(None)).pack(side="left")
        ttk.Button(b, text="Edytuj", command=self.edytuj_modul).pack(side="left", padx=8)
        ttk.Button(b, text="Usun", command=self.usun_modul).pack(side="left")
        ttk.Button(b, text="Pokaz w podgladzie", style="Ok.TButton",
                   command=self.pokaz_modul).pack(side="right")

        prawa = tk.Frame(srodek, bg=BG, width=310)
        prawa.pack(side="left", fill="y", padx=(20, 0))
        prawa.pack_propagate(False)
        tk.Label(prawa, text="Sterownik", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 8))
        karta = tk.Frame(prawa, bg=BG2)
        karta.pack(fill="both", expand=True)

        pol = tk.Frame(karta, bg=BG2)
        pol.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(pol, text="Polaczenie", bg=BG2, fg=FG,
                 font=("Segoe UI Semibold", 10)).pack(side="left")
        self.lbl_sygnal = tk.Label(pol, text="brak — tryb demo", bg=BG2, fg=WARN,
                                   font=("Consolas", 9))
        self.lbl_sygnal.pack(side="right")
        tk.Frame(karta, bg=BG3, height=1).pack(fill="x", padx=16, pady=(6, 12))

        tk.Label(karta, text="Odczyt / zapis danych do sterownika", bg=BG2, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        g1 = tk.Frame(karta, bg=BG2)
        g1.pack(fill="x", padx=16, pady=(8, 4))
        ttk.Button(g1, text="Pobierz ze sterownika",
                   command=lambda: self.sterownik_demo("odczyt")).pack(fill="x", pady=2)
        ttk.Button(g1, text="Wgraj do sterownika", style="Acc.TButton",
                   command=lambda: self.sterownik_demo("zapis")).pack(fill="x", pady=2)

        tk.Frame(karta, bg=BG3, height=1).pack(fill="x", padx=16, pady=12)
        tk.Label(karta, text="Kopia zapasowa ustawien", bg=BG2, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16)
        g2 = tk.Frame(karta, bg=BG2)
        g2.pack(fill="x", padx=16, pady=(8, 4))
        ttk.Button(g2, text="Zapis kopii danych",
                   command=self.kopia_zapis).pack(fill="x", pady=2)
        ttk.Button(g2, text="Odczyt kopii danych",
                   command=self.kopia_odczyt).pack(fill="x", pady=2)

        tk.Frame(karta, bg=BG3, height=1).pack(fill="x", padx=16, pady=12)
        self.lbl_ster = tk.Label(karta, text="", bg=BG2, fg=DIM, anchor="w",
                                 justify="left", font=("Consolas", 9), wraplength=260)
        self.lbl_ster.pack(anchor="w", padx=16, pady=(0, 14))

    def opis_sterownika(self):
        m = self.modul()
        self.lbl_ster.config(
            text=f"kod dostepu:  {m.get('haslo', '')}\n"
                 f"sterowanie:   {m.get('tryb_sterowania', '—')}\n"
                 f"tryb pracy:   {m.get('tryb_pracy', '—')}\n"
                 f"zalaczenie:   {m.get('zalaczenie_s', 1)} s\n"
                 f"wyjscie:      {'impuls' if m.get('tryb') == 'impuls' else 'toggle ON/OFF'}\n"
                 f"czas otwarcia:{m.get('czas_otwarcia', 8)} s")

    # ---------------- WIDOK: STEROWNIK ----------------
    def _karta(self, rodzic, tytul, ikona=""):
        k = tk.Frame(rodzic, bg=BG2)
        naglowek = tk.Frame(k, bg=BG2)
        naglowek.pack(fill="x", padx=16, pady=(12, 0))
        tk.Label(naglowek, text=tytul, bg=BG2, fg=FG,
                 font=("Segoe UI Semibold", 10)).pack(side="left")
        tk.Frame(k, bg=BG3, height=1).pack(fill="x", padx=16, pady=(8, 0))
        wnetrze = tk.Frame(k, bg=BG2)
        wnetrze.pack(fill="both", expand=True, padx=16, pady=12)
        return k, naglowek, wnetrze

    def _buduj_sterownik(self):
        f = self.f_sterownik
        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", padx=20, pady=(6, 10))
        tk.Label(top, text="Sterownik GSM", bg=BG, fg=FG,
                 font=("Segoe UI Semibold", 15)).pack(side="left")
        self.v_obiekt_st = tk.StringVar()
        self.cb_obiekt_st = ttk.Combobox(top, textvariable=self.v_obiekt_st,
                                         state="readonly", width=34)
        self.cb_obiekt_st.pack(side="right")
        self.cb_obiekt_st.bind("<<ComboboxSelected>>", self.zmien_modul_st)

        # ---- POLACZENIE ----
        k1, nag1, w1 = self._karta(f, "Polaczenie")
        k1.pack(fill="x", padx=20)
        self.cv_sygnal = tk.Canvas(nag1, width=64, height=18, bg=BG2,
                                   highlightthickness=0)
        self.cv_sygnal.pack(side="right")
        self.lbl_proc = tk.Label(nag1, text="0%", bg=BG2, fg=DIM,
                                 font=("Segoe UI Semibold", 10))
        self.lbl_proc.pack(side="right", padx=(0, 8))

        lewy1 = tk.Frame(w1, bg=BG2)
        lewy1.pack(side="left")
        self.btn_pol = ttk.Button(lewy1, text="Polacz", style="Acc.TButton",
                                  command=self.przel_polaczenie)
        self.btn_pol.pack(side="left")
        self.lbl_stan_pol = tk.Label(lewy1, text="rozlaczony", bg=BG2, fg=DIM,
                                     font=("Segoe UI", 9))
        self.lbl_stan_pol.pack(side="left", padx=14)

        self.v_logi = tk.BooleanVar(value=False)
        tk.Checkbutton(w1, text="Pokaz logi", variable=self.v_logi, bg=BG2, fg=DIM,
                       selectcolor=BG3, activebackground=BG2, activeforeground=FG,
                       font=("Segoe UI", 9),
                       command=self.przel_logi).pack(side="right")

        # ---- ODCZYT / ZAPIS ----
        k2, _, w2 = self._karta(f, "Odczyt / zapis danych do sterownika")
        k2.pack(fill="x", padx=20, pady=(12, 0))
        siatka = tk.Frame(w2, bg=BG2)
        siatka.pack(fill="x")
        siatka.columnconfigure(0, weight=1)
        siatka.columnconfigure(1, weight=1)
        ttk.Button(siatka, text="Pobierz ze sterownika", style="Ok.TButton",
                   command=lambda: self.sterownik_demo("odczyt")).grid(
                       row=0, column=0, sticky="ew", padx=(0, 6), pady=3)
        ttk.Button(siatka, text="Wgraj do sterownika", style="Acc.TButton",
                   command=lambda: self.sterownik_demo("zapis")).grid(
                       row=0, column=1, sticky="ew", padx=(6, 0), pady=3)
        ttk.Button(siatka, text="Zapis kopii danych",
                   command=self.kopia_zapis).grid(row=1, column=0, sticky="ew",
                                                  padx=(0, 6), pady=3)
        ttk.Button(siatka, text="Odczyt kopii danych",
                   command=self.kopia_odczyt).grid(row=1, column=1, sticky="ew",
                                                   padx=(6, 0), pady=3)

        # ---- KOD DOSTEPU + TRYB STEROWANIA ----
        rz = tk.Frame(f, bg=BG)
        rz.pack(fill="x", padx=20, pady=(12, 0))
        k3, _, w3 = self._karta(rz, "Kod dostepu")
        k3.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.v_kod = tk.StringVar()
        e = ttk.Entry(w3, textvariable=self.v_kod, font=("Consolas", 16),
                      justify="center")
        e.pack(fill="x", ipady=6)
        self.v_kod.trace_add("write", lambda *a: self.zapisz_sterownik())

        k4, _, w4 = self._karta(rz, "Tryb sterowania")
        k4.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.v_ster_tryb = tk.StringVar()
        cb = ttk.Combobox(w4, textvariable=self.v_ster_tryb, state="readonly",
                          values=["CLIP", "SMS", "CLIP+SMS"])
        cb.pack(fill="x", ipady=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self.zapisz_sterownik())

        # ---- TRYB PRACY + KONFIGURACJA WYJSCIA ----
        rz2 = tk.Frame(f, bg=BG)
        rz2.pack(fill="x", padx=20, pady=(12, 0))
        k5, _, w5 = self._karta(rz2, "Tryb pracy")
        k5.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.v_praca = tk.StringVar()
        for val, lab in [("prywatny", "Prywatny"), ("publiczny", "Publiczny")]:
            tk.Radiobutton(w5, text=lab, variable=self.v_praca, value=val, bg=BG2,
                           fg=FG, selectcolor=BG3, activebackground=BG2,
                           activeforeground=FG, font=("Segoe UI", 10),
                           command=self.zapisz_sterownik).pack(side="left", padx=(0, 20))
        self.lbl_praca = tk.Label(w5, text="", bg=BG2, fg=DIM, font=("Segoe UI", 8))
        self.lbl_praca.pack(side="left")

        k6, _, w6 = self._karta(rz2, "Konfiguracja wyjscia")
        k6.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.v_wyjscie = tk.StringVar()
        r1 = tk.Frame(w6, bg=BG2)
        r1.pack(fill="x")
        tk.Radiobutton(r1, text="Zalaczenie (s):", variable=self.v_wyjscie,
                       value="impuls", bg=BG2, fg=FG, selectcolor=BG3,
                       activebackground=BG2, activeforeground=FG,
                       font=("Segoe UI", 10),
                       command=self.zapisz_sterownik).pack(side="left")
        self.v_zal_s = tk.StringVar()
        ttk.Entry(r1, textvariable=self.v_zal_s, width=6).pack(side="left", padx=8)
        self.v_zal_s.trace_add("write", lambda *a: self.zapisz_sterownik())
        tk.Radiobutton(w6, text="Toggle (ON/OFF)", variable=self.v_wyjscie,
                       value="stan", bg=BG2, fg=FG, selectcolor=BG3,
                       activebackground=BG2, activeforeground=FG,
                       font=("Segoe UI", 10),
                       command=self.zapisz_sterownik).pack(anchor="w", pady=(8, 0))

        # ---- LOGI ----
        self.ram_logi = tk.Frame(f, bg=BG)
        tk.Label(self.ram_logi, text="Logi", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(12, 4))
        self.txt_logi = tk.Text(self.ram_logi, bg=BG2, fg=FG, height=7, borderwidth=0,
                                highlightthickness=0, font=("Consolas", 9),
                                padx=12, pady=8)
        self.txt_logi.pack(fill="both", expand=True)

        self.polaczony = False
        self._blok_zapisu = False

    def zmien_modul_st(self, e=None):
        for i, m in enumerate(self.d["moduly"]):
            if m["nazwa"] == self.v_obiekt_st.get():
                self.mod_idx = i
                break
        self.odswiez_sterownik()

    def odswiez_sterownik(self):
        m = self.modul()
        self._blok_zapisu = True
        self.cb_obiekt_st.configure(values=[x["nazwa"] for x in self.d["moduly"]])
        self.v_obiekt_st.set(m["nazwa"])
        self.v_kod.set(m.get("haslo", ""))
        self.v_ster_tryb.set(m.get("tryb_sterowania", "CLIP+SMS"))
        self.v_praca.set(m.get("tryb_pracy", "prywatny"))
        self.v_wyjscie.set(m.get("tryb", "impuls"))
        self.v_zal_s.set(str(m.get("zalaczenie_s", 1)))
        self._blok_zapisu = False
        self.lbl_praca.config(
            text="wpuszcza tylko numery z listy" if self.v_praca.get() == "prywatny"
            else "wpuszcza kazdy numer")
        self.rysuj_sygnal()

    def zapisz_sterownik(self):
        if getattr(self, "_blok_zapisu", False):
            return
        m = self.modul()
        m["haslo"] = self.v_kod.get().strip()
        m["tryb_sterowania"] = self.v_ster_tryb.get()
        m["tryb_pracy"] = self.v_praca.get()
        m["tryb"] = self.v_wyjscie.get()
        try:
            m["zalaczenie_s"] = max(1, min(60, int(self.v_zal_s.get() or 1)))
        except ValueError:
            pass
        zapisz(self.d)
        self.lbl_praca.config(
            text="wpuszcza tylko numery z listy" if self.v_praca.get() == "prywatny"
            else "wpuszcza kazdy numer")
        self.log_ster(f"zmieniono ustawienia: {m['tryb_sterowania']}, "
                      f"{m['tryb_pracy']}, wyjscie {m['tryb']}")

    def rysuj_sygnal(self):
        c = self.cv_sygnal
        c.delete("all")
        proc = 77 if self.polaczony else 0
        self.lbl_proc.config(text=f"{proc}%", fg=OK if self.polaczony else DIM)
        for i in range(5):
            h = 4 + i * 3
            akt = self.polaczony and (i + 1) * 20 <= proc + 10
            c.create_rectangle(4 + i * 12, 16 - h, 12 + i * 12, 16,
                               fill=OK if akt else BG3, outline="")

    def przel_polaczenie(self):
        self.polaczony = not self.polaczony
        if self.polaczony:
            m = self.modul()
            self.btn_pol.config(text="Rozlacz")
            self.lbl_stan_pol.config(text="polaczony (symulacja)", fg=OK)
            self.log_ster(f"polaczono z {m.get('sim') or '(brak numeru SIM)'} — symulacja")
            self.log_ster("odczyt sygnalu: 77%")
        else:
            self.btn_pol.config(text="Polacz")
            self.lbl_stan_pol.config(text="rozlaczony", fg=DIM)
            self.log_ster("rozlaczono")
        self.rysuj_sygnal()

    def przel_logi(self):
        if self.v_logi.get():
            self.ram_logi.pack(fill="both", expand=True, padx=20, pady=(0, 16))
            self.log_ster("wlaczono podglad logow")
        else:
            self.ram_logi.pack_forget()

    def log_ster(self, txt):
        try:
            self.txt_logi.insert("1.0", f"{datetime.now():%H:%M:%S}  {txt}\n")
            if int(self.txt_logi.index("end-1c").split(".")[0]) > 200:
                self.txt_logi.delete("200.0", "end")
        except Exception:
            pass
        self.zdarzenie(txt)

    def sterownik_demo(self, co):
        m = self.modul()
        if co == "odczyt":
            messagebox.showinfo(
                "Tryb demo",
                "Odczyt ustawien ze sterownika bedzie mozliwy po podlaczeniu modulu.\n\n"
                f"Komenda poszlaby na numer SIM: {m.get('sim') or '(nie podano)'}")
        else:
            messagebox.showinfo(
                "Tryb demo",
                "Zapis ustawien do sterownika bedzie mozliwy po podlaczeniu modulu.\n\n"
                f"Do wyslania: kod {m.get('haslo', '')}, "
                f"tryb {m.get('tryb_sterowania', '')}, "
                f"zalaczenie {m.get('zalaczenie_s', 1)} s.")
        self.zdarzenie(f"sterownik ({co}) — tryb demo")

    def kopia_zapis(self):
        sc = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"zapora-kopia-{datetime.now():%Y-%m-%d}.json",
            filetypes=[("Kopia ustawien", "*.json")])
        if not sc:
            return
        try:
            with open(sc, "w", encoding="utf-8") as f:
                json.dump(self.d, f, ensure_ascii=False, indent=2)
            self.zdarzenie("zapisano kopie ustawien")
            messagebox.showinfo("Gotowe",
                                f"Zapisano {len(self.d.get('moduly', []))} obiektow "
                                f"i {len(self.d.get('historia', []))} wpisow historii.")
        except Exception as e:
            messagebox.showerror("Blad", str(e))

    def kopia_odczyt(self):
        sc = filedialog.askopenfilename(filetypes=[("Kopia ustawien", "*.json"),
                                                   ("Wszystkie pliki", "*.*")])
        if not sc:
            return
        try:
            with open(sc, "r", encoding="utf-8") as f:
                nowa = json.load(f)
            if "moduly" not in nowa:
                messagebox.showwarning("Zly plik", "To nie jest kopia ustawien ZAPORA-AWF.")
                return
            ile_m = len(nowa.get("moduly", []))
            ile_h = len(nowa.get("historia", []))
            if not messagebox.askyesno(
                    "Potwierdz",
                    f"Wczytac kopie?\n\nObiektow: {ile_m}\nWpisow historii: {ile_h}\n\n"
                    "Obecne dane zostana zastapione."):
                return
            nowa.setdefault("pin", self.d.get("pin"))
            nowa.setdefault("motyw", self.d.get("motyw", "ciemny"))
            nowa.setdefault("marka", self.d.get("marka"))
            self.d = nowa
            zapisz(self.d)
            self.mod_idx = 0
            self.odswiez_moduly()
            self.zdarzenie(f"wczytano kopie: {ile_m} obiektow")
            messagebox.showinfo("Gotowe", "Kopia wczytana.")
        except Exception as e:
            messagebox.showerror("Blad", str(e))

    def odswiez_moduly(self):
        for i in self.tvm.get_children():
            self.tvm.delete(i)
        for i, m in enumerate(self.d["moduly"]):
            self.tvm.insert("", "end", iid=str(i), tags=("demo",),
                            values=(m.get("nazwa", ""), m.get("sim") or "—",
                                    m.get("typ", ""),
                                    m.get("tryb_sterowania", "—"),
                                    m.get("tryb_pracy", "—"),
                                    f"{m.get('czas_otwarcia', 8)} s",
                                    len(m.get("numery", [])), "demo"))
        try:
            self.opis_sterownika()
        except Exception:
            pass

    def _sel_modul(self):
        s = self.tvm.selection()
        return int(s[0]) if s else None

    def edytuj_modul(self):
        i = self._sel_modul()
        if i is None:
            self.zdarzenie("zaznacz modul")
            return
        self.dialog_modul(i)

    def pokaz_modul(self):
        i = self._sel_modul()
        if i is None:
            return
        self.mod_idx = i
        self.przelacz("podglad")

    def usun_modul(self):
        i = self._sel_modul()
        if i is None:
            return
        if len(self.d["moduly"]) == 1:
            messagebox.showinfo("Nie mozna", "Musi zostac co najmniej jeden modul.")
            return
        m = self.d["moduly"][i]
        if messagebox.askyesno("Potwierdz",
                               f"Usunac obiekt '{m['nazwa']}' razem z lista "
                               f"{len(m.get('numery', []))} numerow?"):
            del self.d["moduly"][i]
            self.mod_idx = 0
            zapisz(self.d)
            self.odswiez_moduly()
            self.zdarzenie(f"usunieto modul: {m['nazwa']}")

    def dialog_modul(self, idx):
        m = self.d["moduly"][idx] if idx is not None else nowy_modul()
        w = tk.Toplevel(self)
        w.title("Modul GSM")
        w.configure(bg=BG2)
        w.geometry("500x860")
        w.transient(self)
        w.grab_set()
        w.resizable(False, False)
        tk.Label(w, text="Modul GSM przy bramie", bg=BG2, fg=FG,
                 font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=24, pady=(18, 8))

        pola = {}
        for k, lab, hint in [("nazwa", "Nazwa obiektu", "np. Brama glowna AWF"),
                             ("sim", "Numer karty SIM w module", "na ten numer ida komendy"),
                             ("haslo", "Haslo modulu", "fabrycznie zwykle 1234")]:
            tk.Label(w, text=lab, bg=BG2, fg=DIM,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(10, 3))
            v = tk.StringVar(value=str(m.get(k, "")))
            ttk.Entry(w, textvariable=v).pack(fill="x", padx=24, ipady=4)
            tk.Label(w, text=hint, bg=BG2, fg=DIM,
                     font=("Segoe UI", 8)).pack(anchor="w", padx=24)
            pola[k] = v

        tk.Label(w, text="Typ modulu", bg=BG2, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(12, 3))
        v_typ = tk.StringVar(value=m.get("typ", TYPY_MODULOW[0]))
        ttk.Combobox(w, textvariable=v_typ, values=TYPY_MODULOW,
                     state="readonly").pack(fill="x", padx=24)

        tk.Label(w, text="STEROWANIE PRZEKAZNIKIEM", bg=BG2, fg=ACC,
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=24, pady=(20, 8))
        v_tryb = tk.StringVar(value=m.get("tryb", "impuls"))
        tr = tk.Frame(w, bg=BG2)
        tr.pack(anchor="w", padx=22)
        for val, lab in [("impuls", "Impuls (brama sama sie zamyka)"),
                         ("stan", "Stan zalaczony (trzyma otwarte)")]:
            tk.Radiobutton(tr, text=lab, variable=v_tryb, value=val, bg=BG2, fg=FG,
                           selectcolor=BG3, activebackground=BG2, activeforeground=FG,
                           font=("Segoe UI", 9)).pack(anchor="w")

        siatka = tk.Frame(w, bg=BG2)
        siatka.pack(anchor="w", padx=24, pady=(12, 0))
        v_imp = tk.StringVar(value=str(m.get("impuls_ms", 500)))
        v_czas = tk.StringVar(value=str(m.get("czas_otwarcia", 8)))
        v_opoz = tk.StringVar(value=str(m.get("opoznienie", 2)))
        for kol, (v, lab) in enumerate([(v_imp, "dlugosc impulsu (ms)"),
                                        (v_czas, "czas otwarcia (s)"),
                                        (v_opoz, "zwloka zamykania (s)")]):
            tk.Label(siatka, text=lab, bg=BG2, fg=DIM,
                     font=("Segoe UI", 8)).grid(row=0, column=kol, sticky="w", padx=(0, 14))
            ttk.Entry(siatka, textvariable=v, width=10).grid(row=1, column=kol,
                                                             sticky="w", padx=(0, 14))
        v_auto = tk.BooleanVar(value=m.get("autozamykanie", True))
        tk.Checkbutton(w, text="Autozamykanie po uplywie czasu otwarcia",
                       variable=v_auto, bg=BG2, fg=FG, selectcolor=BG3,
                       activebackground=BG2, activeforeground=FG,
                       font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(14, 0))

        tk.Label(w, text="STEROWNIK GSM", bg=BG2, fg=ACC,
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=24, pady=(20, 6))
        st = tk.Frame(w, bg=BG2)
        st.pack(anchor="w", padx=24, fill="x")
        tk.Label(st, text="Tryb sterowania", bg=BG2, fg=DIM,
                 font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w", padx=(0, 16))
        tk.Label(st, text="Tryb pracy", bg=BG2, fg=DIM,
                 font=("Segoe UI", 8)).grid(row=0, column=1, sticky="w", padx=(0, 16))
        tk.Label(st, text="Zalaczenie (s)", bg=BG2, fg=DIM,
                 font=("Segoe UI", 8)).grid(row=0, column=2, sticky="w")
        v_ster = tk.StringVar(value=m.get("tryb_sterowania", "CLIP+SMS"))
        ttk.Combobox(st, textvariable=v_ster, state="readonly", width=12,
                     values=["CLIP", "SMS", "CLIP+SMS"]).grid(row=1, column=0,
                                                              sticky="w", padx=(0, 16))
        v_pracy = tk.StringVar(value=m.get("tryb_pracy", "prywatny"))
        ttk.Combobox(st, textvariable=v_pracy, state="readonly", width=12,
                     values=["prywatny", "publiczny"]).grid(row=1, column=1,
                                                            sticky="w", padx=(0, 16))
        v_zal = tk.StringVar(value=str(m.get("zalaczenie_s", 1)))
        ttk.Entry(st, textvariable=v_zal, width=8).grid(row=1, column=2, sticky="w")
        tk.Label(w, text="CLIP = otwiera samo polaczenie.  Publiczny = wpuszcza kazdy numer.",
                 bg=BG2, fg=DIM, font=("Segoe UI", 8)).pack(anchor="w", padx=24, pady=(6, 0))

        v_foto = tk.BooleanVar(value=m.get("zdjecie", True))
        tk.Checkbutton(w, text="Scena z prawdziwego zdjecia wjazdu",
                       variable=v_foto, bg=BG2, fg=FG, selectcolor=BG3,
                       activebackground=BG2, activeforeground=FG,
                       font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(16, 0))
        tk.Label(w, text="odznacz, aby wrocic do sceny rysowanej",
                 bg=BG2, fg=DIM, font=("Segoe UI", 8)).pack(anchor="w", padx=44)

        tk.Label(w, text="Rodzaj przegrody", bg=BG2, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(14, 3))
        v_wyg = tk.StringVar(value=m.get("wyglad", "slupki"))
        wg = tk.Frame(w, bg=BG2)
        wg.pack(anchor="w", padx=22)
        for val, lab in [("slupki", "Slupki chowane w jezdnie"),
                         ("szlaban", "Szlaban"),
                         ("przesuwna", "Brama przesuwna")]:
            tk.Radiobutton(wg, text=lab, variable=v_wyg, value=val, bg=BG2, fg=FG,
                           selectcolor=BG3, activebackground=BG2, activeforeground=FG,
                           font=("Segoe UI", 9)).pack(anchor="w")

        def ok():
            if not pola["nazwa"].get().strip():
                messagebox.showwarning("Brak danych", "Podaj nazwe obiektu.")
                return
            sim = norm_tel(pola["sim"].get()) if pola["sim"].get().strip() else ""
            try:
                imp = max(100, min(5000, int(v_imp.get())))
                int(v_zal.get() or 1)
                czas = max(1, min(300, int(v_czas.get())))
                opoz = max(0, min(60, int(v_opoz.get())))
            except ValueError:
                messagebox.showwarning("Liczby", "Czasy musza byc liczbami calkowitymi.")
                return
            m.update({"nazwa": pola["nazwa"].get().strip(), "sim": sim,
                      "haslo": pola["haslo"].get().strip(), "typ": v_typ.get(),
                      "tryb": v_tryb.get(), "impuls_ms": imp, "czas_otwarcia": czas,
                      "opoznienie": opoz, "autozamykanie": v_auto.get(),
                      "wyglad": v_wyg.get(), "wyglad_wybrany": True,
                      "zdjecie": v_foto.get(),
                      "tryb_sterowania": v_ster.get(), "tryb_pracy": v_pracy.get(),
                      "zalaczenie_s": max(1, min(60, int(v_zal.get() or 1)))})
            m.setdefault("numery", [])
            if idx is None:
                self.d["moduly"].append(m)
                self.zdarzenie(f"dodano modul: {m['nazwa']}")
            else:
                self.zdarzenie(f"zapisano modul: {m['nazwa']}")
            zapisz(self.d)
            self.odswiez_moduly()
            w.destroy()

        bf = tk.Frame(w, bg=BG2)
        bf.pack(fill="x", padx=24, pady=18, side="bottom")
        ttk.Button(bf, text="Zapisz", style="Acc.TButton", command=ok).pack(side="right")
        ttk.Button(bf, text="Anuluj", command=w.destroy).pack(side="right", padx=8)
        w.bind("<Escape>", lambda e: w.destroy())

    def _etykieta_motywu(self):
        return "Tryb jasny" if self.d.get("motyw", "ciemny") == "ciemny" else "Tryb ciemny"

    def przelacz_motyw(self):
        nowy = "jasny" if self.d.get("motyw", "ciemny") == "ciemny" else "ciemny"
        self.d["motyw"] = nowy
        zapisz(self.d)
        ustaw_motyw(nowy)
        self.configure(bg=BG)
        for w in self.winfo_children():
            w.destroy()
        self._styl()
        self._ui()
        self.przelacz(self.widok)
        self.zdarzenie(f"motyw: {nowy}")

    # ---------------- EMBLEMAT (gdy brak logo.png) ----------------
    def emblemat(self, cv, S):
        cv.create_oval(2, 2, S - 2, S - 2, fill="#132034", outline=ACC, width=2)
        cv.create_rectangle(S * .30, S * .58, S * .38, S * .78, fill="#48525f", outline="")
        cv.create_oval(S * .28, S * .46, S * .41, S * .58, fill="#f2b544", outline="")
        import math as _m
        px, py, L, gr = S * .36, S * .60, S * .42, S * .05
        k = _m.radians(35)
        for i in range(4):
            t1, t2 = i / 4 * L, (i + 1) / 4 * L
            pts = []
            for t, off in ((t1, -gr), (t2, -gr), (t2, gr), (t1, gr)):
                pts += [px + t * _m.cos(k) + off * _m.sin(k),
                        py - t * _m.sin(k) + off * _m.cos(k)]
            cv.create_polygon(pts, fill="#d93b40" if i % 2 == 0 else "#f0f4f9", outline="")

    # ---------------- LOGOWANIE PIN ----------------
    def ekran_logowania(self, po_zablokowaniu=False):
        w = tk.Toplevel(self)
        w.title("Logowanie")
        w.configure(bg=BG2)
        w.geometry("360x520")
        w.resizable(False, False)
        ico = zasob("ikona.ico")
        if ico:
            try:
                w.iconbitmap(ico)
            except Exception:
                pass
        w.update_idletasks()
        x = (w.winfo_screenwidth() - 360) // 2
        y = (w.winfo_screenheight() - 520) // 2
        w.geometry(f"+{x}+{y}")
        w.protocol("WM_DELETE_WINDOW", lambda: (w.destroy(), self.destroy()))
        w.grab_set()

        cv = tk.Canvas(w, width=64, height=64, bg=BG2, highlightthickness=0)
        cv.pack(pady=(26, 8))
        self.emblemat(cv, 64)
        tk.Label(w, text=self.d["marka"]["nazwa"], bg=BG2, fg=FG,
                 font=("Segoe UI Semibold", 13)).pack()
        tk.Label(w, text="Podaj PIN dostepu", bg=BG2, fg=DIM,
                 font=("Segoe UI", 10)).pack(pady=(4, 0))

        kropki = tk.Label(w, text="", bg=BG2, fg=ACC, font=("Segoe UI", 24))
        kropki.pack(pady=(16, 2))
        info = tk.Label(w, text="", bg=BG2, fg="#d6444a", font=("Segoe UI", 9))
        info.pack()

        stan = {"pin": "", "proby": 0}

        def pokaz():
            kropki.config(text="●  " * len(stan["pin"]))

        def wpisz(c):
            if len(stan["pin"]) < 8:
                stan["pin"] += c
                pokaz()

        def kasuj():
            stan["pin"] = stan["pin"][:-1]
            pokaz()
            info.config(text="")

        def zatwierdz():
            ok, nowy_skrot = pin_pasuje(stan["pin"], self.d.get("pin"))
            if ok:
                if nowy_skrot:
                    self.d["pin"] = nowy_skrot
                    zapisz(self.d)
                w.destroy()
                self.deiconify()
                self.lift()
                self.zdarzenie("zalogowano" if not po_zablokowaniu else "odblokowano")
            else:
                stan["proby"] += 1
                stan["pin"] = ""
                pokaz()
                info.config(text=f"Bledny PIN  (proba {stan['proby']}/5)")
                if stan["proby"] >= 5:
                    messagebox.showerror("Zablokowano",
                                         "Pieciokrotnie bledny PIN. Program zostanie zamkniety.")
                    w.destroy()
                    self.destroy()

        klaw = tk.Frame(w, bg=BG2)
        klaw.pack(pady=(14, 0))
        uklad = [("1", "2", "3"), ("4", "5", "6"), ("7", "8", "9"), ("C", "0", "OK")]
        for r, rzad in enumerate(uklad):
            for c, znak in enumerate(rzad):
                if znak == "C":
                    kol, akcja = mix(BG3, "#d6444a", 0.25), kasuj
                elif znak == "OK":
                    kol, akcja = mix(BG3, OK, 0.35), zatwierdz
                else:
                    kol, akcja = BG3, (lambda z=znak: wpisz(z))
                b = tk.Label(klaw, text=znak, bg=kol, fg=FG,
                             font=("Segoe UI Semibold", 16), width=4, height=2,
                             cursor="hand2")
                b.grid(row=r, column=c, padx=5, pady=5)
                b.bind("<Button-1>", lambda e, a=akcja: a())

        tk.Label(w, text="PIN fabryczny: 1234  —  zmien po pierwszym logowaniu",
                 bg=BG2, fg=DIM, font=("Segoe UI", 8)).pack(pady=(16, 0))

        w.bind("<Key>", lambda e: wpisz(e.char) if e.char.isdigit() else None)
        w.bind("<BackSpace>", lambda e: kasuj())
        w.bind("<Return>", lambda e: zatwierdz())
        w.focus_force()

    def zablokuj(self):
        self.withdraw()
        self.ekran_logowania(po_zablokowaniu=True)

    def okno_pin(self):
        w = tk.Toplevel(self)
        w.title("Zmiana PIN")
        w.configure(bg=BG2)
        w.geometry("400x300")
        w.resizable(False, False)
        w.transient(self)
        w.grab_set()
        tk.Label(w, text="Zmiana kodu PIN", bg=BG2, fg=FG,
                 font=("Segoe UI Semibold", 13)).pack(anchor="w", padx=24, pady=(20, 6))
        pola = {}
        for k, lab in [("stary", "Obecny PIN"), ("nowy", "Nowy PIN (4-8 cyfr)"),
                       ("powt", "Powtorz nowy PIN")]:
            tk.Label(w, text=lab, bg=BG2, fg=DIM,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(10, 3))
            v = tk.StringVar()
            ttk.Entry(w, textvariable=v, show="●").pack(fill="x", padx=24, ipady=4)
            pola[k] = v

        def zapisz_pin():
            if not pin_pasuje(pola["stary"].get(), self.d.get("pin"))[0]:
                messagebox.showwarning("Blad", "Obecny PIN jest niepoprawny.")
                return
            n = pola["nowy"].get().strip()
            if not n.isdigit() or not 4 <= len(n) <= 8:
                messagebox.showwarning("Blad", "Nowy PIN musi miec 4-8 cyfr.")
                return
            if n != pola["powt"].get().strip():
                messagebox.showwarning("Blad", "Powtorzony PIN sie nie zgadza.")
                return
            self.d["pin"] = hasz_pin(n)
            zapisz(self.d)
            self.zdarzenie("zmieniono PIN")
            messagebox.showinfo("Gotowe", "PIN zostal zmieniony.")
            w.destroy()

        bf = tk.Frame(w, bg=BG2)
        bf.pack(fill="x", padx=24, pady=20)
        ttk.Button(bf, text="Zapisz", style="Acc.TButton",
                   command=zapisz_pin).pack(side="right")
        ttk.Button(bf, text="Anuluj", command=w.destroy).pack(side="right", padx=8)

    # ---------------- INSTRUKCJA ----------------
    def okno_instrukcja(self):
        w = tk.Toplevel(self)
        w.title("Instrukcja obslugi")
        w.configure(bg=BG)
        w.geometry("760x640")
        w.transient(self)
        tk.Label(w, text="Instrukcja obslugi", bg=BG, fg=FG,
                 font=("Segoe UI Semibold", 15)).pack(anchor="w", padx=24, pady=(20, 2))
        tk.Label(w, text="Co robi kazdy przycisk i gdzie sie co zapisuje",
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w", padx=24)

        ram = tk.Frame(w, bg=BG)
        ram.pack(fill="both", expand=True, padx=24, pady=16)
        sb = tk.Scrollbar(ram)
        sb.pack(side="right", fill="y")
        txt = tk.Text(ram, bg=BG2, fg=FG, borderwidth=0, highlightthickness=0,
                      font=("Segoe UI", 10), wrap="word", padx=18, pady=16,
                      yscrollcommand=sb.set, spacing1=2, spacing3=6)
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)

        txt.tag_configure("h", font=("Segoe UI Semibold", 12), foreground=ACC,
                          spacing1=14, spacing3=6)
        txt.tag_configure("b", font=("Segoe UI Semibold", 10), foreground=FG)
        txt.tag_configure("d", foreground=DIM)

        tresc = [
            ("h", "LOGOWANIE"),
            ("", "Program otwiera sie ekranem PIN. Fabryczny kod to 1234 — zmien go od razu "
                 "przyciskiem Zmien PIN w prawym gornym rogu. Piec blednych prob zamyka program. "
                 "Przycisk Zablokuj chowa okno i wraca do ekranu PIN, gdy odchodzisz od komputera."),
            ("h", "WIDOK: PODGLAD"),
            ("b", "SYMULUJ PRZEJAZD"),
            ("", "Odpala pelna sekwencje: auto podjezdza, na ekranie pojawia sie imie i numer "
                 "osoby zaznaczonej na liscie, szlaban sie podnosi, auto przejezdza, szlaban opada. "
                 "Zdarzenie trafia do historii."),
            ("b", "Otworz / Zamknij"),
            ("", "Sterowanie samym ramieniem, bez auta. Mozna zatrzymac w polowie i cofnac — "
                 "animacja podejmie od aktualnego kata. Reczne otwarcie tez idzie do historii, "
                 "ale oznaczone jako Obsluga."),
            ("b", "Lista numerow uprawnionych"),
            ("", "Dodaj / Edytuj / Usun. Dwuklik na wierszu otwiera edycje. Numer telefonu "
                 "mozna wpisac jakkolwiek — 601234567, 601-234-567, 0048601234567 — program "
                 "sam sprowadza go do formatu +48601234567. Kolumny WJAZDOW i OSTATNIO licza "
                 "sie automatycznie z historii."),
            ("d", "Usuniecie osoby nie kasuje jej historii — raporty za poprzednie miesiace "
                  "pozostaja prawidlowe."),
            ("h", "WIDOK: HISTORIA I RAPORTY"),
            ("b", "Kafelki"),
            ("", "Dzisiaj, ostatnie 7 dni, ten miesiac, lacznie oraz osoba ktora wjezdza najczesciej."),
            ("b", "Filtry"),
            ("", "Wybierz kierowce z listy albo podaj zakres dat w formacie RRRR-MM-DD "
                 "(np. 2026-07-01). Enter w polu daty od razu filtruje. "
                 "Wyczysc filtry wraca do calosci."),
            ("b", "Raport do wydruku"),
            ("", "Tworzy strone HTML i otwiera ja w przegladarce: podsumowanie, godzina szczytu "
                 "ruchu, ranking wjazdow z paskami i pelna lista zdarzen. W przegladarce "
                 "Ctrl+P — masz wydruk albo PDF dla klienta lub wspolnoty."),
            ("b", "Eksport CSV"),
            ("", "Zapisuje to co widac po filtrze. Otwiera sie w Excelu bez ustawiania kodowania."),
            ("h", "GDZIE SA DANE"),
            ("", "Wszystko lezy w folderze %APPDATA%\\ZAPORA-AWF — wklej to w pasek adresu "
                 "Eksploratora Windows."),
            ("d", "baza.json — numery, historia i zahaszowany PIN\n"
                  "raport.html — ostatnio wygenerowany raport"),
            ("", "Zeby przeniesc baze na inny komputer, skopiuj plik baza.json."),
            ("h", "WLASNE LOGO"),
            ("", "Polóz plik logo.png obok programu (obok pliku .exe albo .py) — pojawi sie "
                 "w lewym gornym rogu zamiast domyslnego emblematu. Najlepiej wyglada obrazek "
                 "o wysokosci okolo 50 pikseli, z przezroczystym tlem."),
            ("h", "OBECNY STAN"),
            ("", "To jest wersja symulacyjna. Zapora na ekranie to animacja, program nie jest "
                 "jeszcze polaczony z fizycznym modulem GSM przy bramie. Historia i raporty "
                 "dzialaja juz w pelni — dane zbierane teraz beda widoczne rowniez po podlaczeniu "
                 "prawdziwego sprzetu."),
        ]
        for tag, linia in tresc:
            txt.insert("end", linia + "\n", tag if tag else ())
        txt.config(state="disabled")
        ttk.Button(w, text="Zamknij", command=w.destroy).pack(pady=(0, 20))

    # ---------------- O PROGRAMIE ----------------
    def okno_o_programie(self):
        w = tk.Toplevel(self)
        w.title("O programie")
        w.configure(bg=BG2)
        w.geometry("460x430")
        w.resizable(False, False)
        w.transient(self)
        cv = tk.Canvas(w, width=64, height=64, bg=BG2, highlightthickness=0)
        cv.pack(pady=(24, 10))
        self.emblemat(cv, 64)
        tk.Label(w, text=APP, bg=BG2, fg=FG,
                 font=("Segoe UI Semibold", 15)).pack()
        tk.Label(w, text=f"wersja {VER}   ·   {DATA_WYD}", bg=BG2, fg=ACC,
                 font=("Segoe UI Semibold", 10)).pack(pady=(4, 18))

        karta = tk.Frame(w, bg=BG3)
        karta.pack(fill="x", padx=28)
        dane = [("Wydawca", "AWF Warszawa"),
                ("Wdrozenie", self.d["marka"]["nazwa"]),
                ("Tryb pracy", "skompilowany .exe" if getattr(sys, "frozen", False)
                 else "skrypt Python"),
                ("Python", platform_wersja()),
                ("Numerow w bazie", str(len(self.d.get("numery", [])))),
                ("Wpisow w historii", str(len(self.d.get("historia", [])))),
                ("Katalog danych", kat_dir())]
        for k, v in dane:
            r = tk.Frame(karta, bg=BG3)
            r.pack(fill="x", padx=16, pady=5)
            tk.Label(r, text=k, bg=BG3, fg=DIM, font=("Segoe UI", 9),
                     width=17, anchor="w").pack(side="left")
            tk.Label(r, text=v, bg=BG3, fg=FG, font=("Segoe UI", 9),
                     anchor="w", wraplength=230, justify="left").pack(side="left")

        tk.Label(w, text="Wersja symulacyjna — bez polaczenia z modulem GSM",
                 bg=BG2, fg=WARN, font=("Segoe UI", 9)).pack(pady=(18, 0))
        ttk.Button(w, text="Zamknij", command=w.destroy).pack(pady=16)

    def koniec(self):
        zapisz(self.d)
        self.destroy()


if __name__ == "__main__":
    wlacz_dpi()
    App().mainloop()
