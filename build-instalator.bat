@echo off
chcp 65001 >nul
title ZAPORA-AWF - budowanie instalatora
echo.
echo ============================================
echo   Budowanie instalatora ZAPORA-AWF
echo ============================================
echo.
where python >nul 2>&1
if errorlevel 1 (
    echo [BLAD] Nie znaleziono Pythona.
    echo Pobierz z https://www.python.org/downloads/
    echo WAZNE: zaznacz "Add python.exe to PATH".
    pause
    exit /b 1
)
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo [BLAD] Nie znaleziono Inno Setup 6.
    echo Pobierz: https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)
echo [1/4] Instalacja PyInstaller...
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade pyinstaller --quiet
echo [2/4] Budowanie aplikacji...
python -m PyInstaller --onedir --windowed --clean --noupx --name "ZAPORA-AWF" --icon ikona.ico --version-file wersja.txt --manifest manifest.xml --add-data "ikona.ico;." --add-data "logo.png;." zapora_awf.py
if errorlevel 1 ( echo [BLAD] Kompilacja nie powiodla sie. & pause & exit /b 1 )
echo [3/4] Budowanie instalatora...
%ISCC% instalator.iss
if errorlevel 1 ( echo [BLAD] Instalator nie powstal. & pause & exit /b 1 )
echo [4/4] Sprzatanie...
rmdir /s /q build 2>nul
del /q "ZAPORA-AWF.spec" 2>nul
echo.
echo   Instalator:  %CD%\ZAPORA-AWF-Instalator-v4.8.exe
echo   PIN fabryczny: 1234
explorer "%CD%"
pause
