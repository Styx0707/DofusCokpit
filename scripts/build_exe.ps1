# Builds DofusCockpit.exe (the launcher) via PyInstaller.
# Usage (project root): powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1
# Recommended: Python 3.11 or 3.12 (PyInstaller may lag on very new versions).
param([string]$Py = "py")

& $Py -m pip install --upgrade pyinstaller
& $Py -m PyInstaller --onefile --noconsole --name DofusCockpit `
    --distpath . --workpath build\_pyi --specpath build\_pyi launcher.py
if (!(Test-Path DofusCockpit.exe)) { Write-Error "PyInstaller build failed"; exit 1 }

Write-Host ""
Write-Host "OK -> DofusCockpit.exe (project root). Keep it next to docker-compose.yml."
