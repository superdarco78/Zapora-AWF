@echo off
chcp 65001 >nul
title ZAPORA-AWF - uruchomienie testowe
echo.
echo ========================================
echo   ZAPORA-AWF - test na zywo
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [BLAD] Nie znaleziono Pythona.
    echo.
    echo Pobierz z https://www.python.org/downloads/
    echo WAZNE: przy instalacji zaznacz "Add python.exe to PATH"
    echo.
    pause
    exit /b 1
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Instaluje brakujaca biblioteke Pillow... ^(jednorazowo^)
    python -m pip install --quiet pillow
    if errorlevel 1 (
        echo [BLAD] Nie udalo sie zainstalowac Pillow.
        pause
        exit /b 1
    )
    echo Gotowe.
    echo.
)

echo Uruchamiam aplikacje...
echo PIN fabryczny: 1234
echo.
python zapora_awf.py
if errorlevel 1 (
    echo.
    echo [BLAD] Aplikacja zakonczyla sie bledem. Skopiuj tekst powyzej.
    pause
)
