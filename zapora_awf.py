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
VER = "4.4"
DATA_WYD = "27.07.2026"

# paleta
BG, BG2, BG3 = "#0e1217", "#161c24", "#212a35"
FG, DIM, ACC = "#e8eef6", "#7d8b9c", "#3b8ff5"
OK, WARN = "#37c76a", "#e8a33d"


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
            "wyglad": "szlaban", "numery": []}


def sprawdz_dostep(n, teraz=None):
    """Czy ten numer ma teraz prawo otworzyc? Zwraca (tak/nie, powod)."""
    teraz = teraz or datetime.now()
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
                for n in m.get("numery", []):
                    n.setdefault("aktywny", True)
                    n.setdefault("dni", list(DNI))
                    n.setdefault("godz_od", "00:00")
                    n.setdefault("godz_do", "23:59")
                    n.setdefault("wazny_do", "")
            d.setdefault("pin", hasz_pin("1234"))
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
        return {"historia": [], "pin": hasz_pin("1234"), "moduly": [m],
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
        super().__init__(master, bg="#0a0e14", height=self.H,
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

        # --- niebo o zmierzchu ---
        self._gradient(0, 0, W, GY - 60, "#0a1220", "#1d2f4a", 40)
        self._gradient(0, GY - 60, W, GY, "#1d2f4a", "#3a3550", 16)
        # lampy uliczne w tle
        for lx in (120, W - 160):
            self.create_line(lx, GY, lx, GY - 190, fill="#141a22", width=5)
            self.create_line(lx, GY - 190, lx + 34, GY - 196, fill="#141a22", width=4)
            self._poswiata(lx + 36, GY - 194, 46, "#e8a33d", 8)
        # plot / krzaki w tle
        for bx in range(0, W, 46):
            self.create_rectangle(bx, GY - 34, bx + 34, GY - 4,
                                  fill="#121820", outline="")

        # --- jezdnia ---
        self._gradient(0, GY, W, self.H, "#252a31", "#181c22", 12)
        self.create_line(0, GY, W, GY, fill="#39424e", width=2)
        for x in range(-30, W, 78):
            self.create_rectangle(x, GY + 46, x + 40, GY + 52,
                                  fill="#4a5460", outline="")
        # krawezniki
        self.create_rectangle(0, GY - 6, W, GY, fill="#333a44", outline="")

        px = self.PX
        kat = math.radians(self.postep * self.KAT_MAX)

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

    def rysuj_slupki(self, px, GY, p, mig):
        """Slupki blokujace chowane w jezdnie — typ przemyslowy ze stali szczotkowanej.

        p = 0  -> wysuniete (przejazd zamkniety)
        p = 1  -> schowane w jezdni (przejazd wolny)
        """
        WYS = 116         # wysokosc nad jezdnia
        SZER = 26         # srednica korpusu
        pozycje = [px - 108, px, px + 108]
        widoczne = WYS * (1.0 - p)
        pasm = 13

        def slup_kolor(t):
            """Cieniowanie walca: odblask lekko na lewo od srodka."""
            j = 1.0 - abs(t - 0.34) / 0.66
            j = max(0.0, j)
            if t < 0.34:
                return mix("#7a8794", "#eef3f8", j ** 0.9)
            return mix("#59636f", "#eef3f8", j ** 1.15)

        for sx in pozycje:
            # --- plyta bazowa wpuszczona w nawierzchnie ---
            self.create_oval(sx - SZER / 2 - 17, GY - 7, sx + SZER / 2 + 17, GY + 11,
                             fill="#333a44", outline="#4b5562")
            self.create_oval(sx - SZER / 2 - 12, GY - 5, sx + SZER / 2 + 12, GY + 8,
                             fill="#262c34", outline="#3c444f")

            if widoczne < 4:
                # schowany — pokrywa rowno z bruk
                self.create_oval(sx - SZER / 2 - 1, GY - 3, sx + SZER / 2 + 1, GY + 6,
                                 fill="#1f242b", outline="#4b5562")
                continue

            gora = GY - widoczne

            if mig:
                kol_led = "#f2b544"
            elif p > 0.9:
                kol_led = "#37c76a"
            else:
                kol_led = "#e5484d"

            # --- cien na nawierzchni ---
            self.create_oval(sx - SZER / 2 - 6, GY - 4,
                             sx + SZER / 2 + 20 + widoczne * 0.42, GY + 10,
                             fill="#0e1218", outline="")

            # --- poswiata LED ZA korpusem: widac tylko obrys swiatla ---
            self._poswiata(sx, gora + 13, 17, kol_led, 5)

            # --- korpus ze stali szczotkowanej ---
            for i in range(pasm):
                t = i / (pasm - 1.0)
                x1 = sx - SZER / 2 + t * SZER
                x2 = sx - SZER / 2 + (t + 1.0 / (pasm - 1)) * SZER
                self.create_rectangle(x1, gora + 6, x2 + 1, GY + 4,
                                      fill=slup_kolor(t), outline="")
            # delikatne rysy szczotkowania
            for yy in range(int(gora) + 22, int(GY), 13):
                self.create_line(sx - SZER / 2 + 3, yy, sx + SZER / 2 - 3, yy,
                                 fill="#8d99a6", width=1)

            # --- pas odblaskowy tuz pod glowica ---
            yb = gora + 20
            if yb + 9 < GY:
                for i in range(pasm):
                    t = i / (pasm - 1.0)
                    x1 = sx - SZER / 2 + t * SZER
                    x2 = sx - SZER / 2 + (t + 1.0 / (pasm - 1)) * SZER
                    j = max(0.0, 1.0 - abs(t - 0.34) / 0.66)
                    baza = "#d33c40" if 0.18 < t < 0.42 or 0.62 < t < 0.86 else "#f2f5f9"
                    self.create_rectangle(x1, yb, x2 + 1, yb + 9,
                                          fill=mix(baza, "#ffffff", j * 0.30), outline="")

            # --- szczeliny sygnalizacji LED w plaszczu ---
            for dx in (-7, 0, 7):
                self.create_rectangle(sx + dx - 2, gora + 10, sx + dx + 2, gora + 16,
                                      fill=kol_led, outline="")

            # --- czarna glowica ---
            self.create_rectangle(sx - SZER / 2, gora + 2, sx + SZER / 2, gora + 9,
                                  fill="#20262e", outline="")
            self.create_oval(sx - SZER / 2, gora - 4, sx + SZER / 2, gora + 8,
                             fill="#181d24", outline="#39424e")
            self.create_oval(sx - SZER / 2 + 5, gora - 2, sx + SZER / 2 - 5, gora + 4,
                             fill="#2b323b", outline="")

        # --- znak zakazu wjazdu przy krawedzi ---
        zx = px + 196
        self.create_line(zx, GY, zx, GY - 96, fill="#39424e", width=4)
        self.create_oval(zx - 20, GY - 130, zx + 20, GY - 90,
                         fill="#c9302f" if p < 0.5 else "#2a3038",
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
                "odmowa": ("DOSTEP ZABLOKOWANY", "#e05a5f"),
                "cofa": ("DOSTEP ZABLOKOWANY", "#e05a5f")}.get(self.faza, ("GOTOWY", DIM))
        # panel lewy
        self.create_rectangle(18, 18, 300, 88, fill="#0d141d", outline="#243040")
        self.create_text(34, 40, text="BRAMA GLOWNA", anchor="w", fill=FG,
                         font=("Segoe UI Semibold", 12))
        self.create_text(34, 66, text=datetime.now().strftime("%d.%m.%Y   %H:%M:%S"),
                         anchor="w", fill=DIM, font=("Consolas", 10))
        # panel prawy - stan
        wys = 146 if self.powod else (118 if self.kto else 74)
        self.create_rectangle(W - 340, 18, W - 18, wys,
                              fill="#0d141d", outline="#243040")
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
                             fill="#e05a5f", font=("Segoe UI", 9))
        # informacja o trybie przekaznika
        self.create_text(20, self.H - 22,
                         text=("przekaznik: impuls" if self.tryb == "impuls"
                               else "przekaznik: stan zalaczony")
                              + f"   ·   czas otwarcia {self.czas_otwarcia} s"
                              + ("   ·   autozamykanie" if self.autozamykanie
                                 else "   ·   BEZ autozamykania"),
                         anchor="w", fill="#54606e", font=("Consolas", 9))
        # pasek postepu ramienia
        bw = 200
        self.create_rectangle(W - 340, self.H - 40, W - 340 + bw, self.H - 30,
                              fill="#151c26", outline="#243040")
        self.create_rectangle(W - 340, self.H - 40,
                              W - 340 + bw * self.postep, self.H - 30,
                              fill=ACC, outline="")
        self.create_text(W - 130, self.H - 35, text=f"{int(self.postep * 100)}%",
                         anchor="w", fill=DIM, font=("Consolas", 9))

    # ---------- animacja ----------
    def _petla(self):
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
                     ("historia", "HISTORIA I RAPORTY")]:
            b = tk.Label(head, text=t, bg=BG, fg=DIM, font=("Segoe UI Semibold", 10),
                         padx=18, pady=8, cursor="hand2")
            b.pack(side="left", padx=(0, 6))
            b.bind("<Button-1>", lambda e, kk=k: self.przelacz(kk))
            self.tabs[k] = b

        prawy = tk.Frame(head, bg=BG)
        prawy.pack(side="right")
        for txt, cmd in [("?  Instrukcja", self.okno_instrukcja),
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
        self.f_historia = tk.Frame(self.kontener, bg=BG)
        self._buduj_podglad()
        self._buduj_moduly()
        self._buduj_historie()
        self.przelacz("podglad")

    def przelacz(self, k):
        self.widok = k
        for kk, b in self.tabs.items():
            b.config(fg=FG if kk == k else DIM, bg=BG3 if kk == k else BG)
        for f in (self.f_podglad, self.f_moduly, self.f_historia):
            f.pack_forget()
        if k == "podglad":
            self.odswiez()
            self.f_podglad.pack(fill="both", expand=True)
        elif k == "moduly":
            self.odswiez_moduly()
            self.f_moduly.pack(fill="both", expand=True)
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
        self.lbl_sim = tk.Label(wyb, text="", bg=BG, fg="#54606e",
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
        self.tv.tag_configure("blok", foreground="#e05a5f")
        self.tv.tag_configure("ogr", foreground="#e8a33d")
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
        tk.Label(fl, text="(RRRR-MM-DD)", bg=BG, fg="#54606e",
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
        self.tvh.tag_configure("reczne", foreground="#e8a33d")

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

        for i in self.tv.get_children():
            self.tv.delete(i)
        for i, n in enumerate(m.get("numery", [])):
            ile, ost = self._stat_osoby(n.get("imie", ""))
            ok, powod = sprawdz_dostep(n)
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
                 bg=BG2, fg="#54606e", font=("Segoe UI", 8)).pack(anchor="w",
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
        ok, powod = sprawdz_dostep(n)
        self.scena.parametry(m)
        self.scena.przejazd(n.get("imie", "?"), n.get("tel", ""), ok, powod)
        self.zapisz_wjazd(n.get("imie", "?"), n.get("tel", ""),
                          "przejazd (telefon)" if ok else f"ODMOWA — {powod}")

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

        pas = tk.Frame(f, bg="#2a2418")
        pas.pack(fill="x", padx=20, pady=(0, 12))
        tk.Label(pas, text="  TRYB DEMO — moduly nie sa jeszcze polaczone przez internet. "
                           "Ustawienia sa zapisywane i beda wyslane do sprzetu po podlaczeniu.",
                 bg="#2a2418", fg="#e8a33d", font=("Segoe UI", 9),
                 anchor="w", pady=9).pack(fill="x")

        srodek = tk.Frame(f, bg=BG)
        srodek.pack(fill="both", expand=True, padx=20)

        lewa = tk.Frame(srodek, bg=BG)
        lewa.pack(side="left", fill="both", expand=True)
        cols = ("nazwa", "sim", "typ", "tryb", "czas", "auto", "ile", "stan")
        self.tvm = ttk.Treeview(lewa, columns=cols, show="headings", height=9)
        for c, t, w, a in [("nazwa", "OBIEKT", 175, "w"), ("sim", "KARTA SIM", 130, "w"),
                           ("typ", "TYP MODULU", 155, "w"), ("tryb", "PRZEKAZNIK", 95, "w"),
                           ("czas", "CZAS OTW.", 85, "center"),
                           ("auto", "AUTOZAMYK.", 95, "center"),
                           ("ile", "NUMEROW", 80, "center"),
                           ("stan", "POLACZENIE", 100, "center")]:
            self.tvm.heading(c, text=t)
            self.tvm.column(c, width=w, anchor=a)
        self.tvm.tag_configure("demo", foreground="#e8a33d")
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
        tk.Label(prawa, text="Co bedzie po podlaczeniu sprzetu", bg=BG, fg=DIM,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 8))
        karta = tk.Frame(prawa, bg=BG2)
        karta.pack(fill="both", expand=True)
        opisy = [
            ("Dodawanie numerow przez SMS",
             "program wysle komende do karty SIM w module"),
            ("Sterowanie przekaznikiem",
             "otwarcie zdalnie z tego okna, bez dzwonienia"),
            ("Czas otwarcia i autozamykanie",
             "ustawienia zostana zapisane w module"),
            ("Harmonogram",
             "moduly z pamiecia czasowa dostana ograniczenia; "
             "pozostale beda pilnowane przez program"),
            ("Stan polaczenia",
             "odczyt zasiegu GSM i stanu wejsc"),
        ]
        for tyt, opis in opisy:
            tk.Label(karta, text="•  " + tyt, bg=BG2, fg=FG, anchor="w",
                     font=("Segoe UI Semibold", 9),
                     wraplength=270, justify="left").pack(anchor="w", padx=16, pady=(14, 2))
            tk.Label(karta, text=opis, bg=BG2, fg=DIM, anchor="w",
                     font=("Segoe UI", 9), wraplength=270,
                     justify="left").pack(anchor="w", padx=26)

    def odswiez_moduly(self):
        for i in self.tvm.get_children():
            self.tvm.delete(i)
        for i, m in enumerate(self.d["moduly"]):
            self.tvm.insert("", "end", iid=str(i), tags=("demo",),
                            values=(m.get("nazwa", ""), m.get("sim") or "—",
                                    m.get("typ", ""),
                                    "impuls" if m.get("tryb") == "impuls" else "stan",
                                    f"{m.get('czas_otwarcia', 8)} s",
                                    "tak" if m.get("autozamykanie") else "nie",
                                    len(m.get("numery", [])), "demo"))

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
        w.geometry("500x640")
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
            tk.Label(w, text=hint, bg=BG2, fg="#54606e",
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
                czas = max(1, min(300, int(v_czas.get())))
                opoz = max(0, min(60, int(v_opoz.get())))
            except ValueError:
                messagebox.showwarning("Liczby", "Czasy musza byc liczbami calkowitymi.")
                return
            m.update({"nazwa": pola["nazwa"].get().strip(), "sim": sim,
                      "haslo": pola["haslo"].get().strip(), "typ": v_typ.get(),
                      "tryb": v_tryb.get(), "impuls_ms": imp, "czas_otwarcia": czas,
                      "opoznienie": opoz, "autozamykanie": v_auto.get(),
                      "wyglad": v_wyg.get()})
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
        info = tk.Label(w, text="", bg=BG2, fg="#e05a5f", font=("Segoe UI", 9))
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
                    kol, akcja = "#3a2a2e", kasuj
                elif znak == "OK":
                    kol, akcja = "#1c5c33", zatwierdz
                else:
                    kol, akcja = BG3, (lambda z=znak: wpisz(z))
                b = tk.Label(klaw, text=znak, bg=kol, fg=FG,
                             font=("Segoe UI Semibold", 16), width=4, height=2,
                             cursor="hand2")
                b.grid(row=r, column=c, padx=5, pady=5)
                b.bind("<Button-1>", lambda e, a=akcja: a())

        tk.Label(w, text="PIN fabryczny: 1234  —  zmien po pierwszym logowaniu",
                 bg=BG2, fg="#5c6672", font=("Segoe UI", 8)).pack(pady=(16, 0))

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
