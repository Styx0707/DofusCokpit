@echo off
rem Lance le daemon walker (auto-clic). Double-clic, ou appele via le protocole
rem dofuswalker: depuis live.html. Le garde-fou _Singleton evite les doublons.
setlocal
set "AU=C:\Program Files (x86)\AutoIt3\AutoIt3.exe"
if not exist "%AU%" set "AU=C:\Program Files\AutoIt3\AutoIt3.exe"
if not exist "%AU%" (
    echo AutoIt3.exe introuvable - installe AutoIt ou corrige le chemin dans start_walker.bat
    pause
    exit /b 1
)
start "" "%AU%" "%~dp0dofus_walker.au3"
