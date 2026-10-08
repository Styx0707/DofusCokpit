# Builds a ready-to-copy .zip: project + DofusCockpit.exe + DB dump + icons,
# WITHOUT .git / build / caches / dev captures.
# Usage (project root): powershell -ExecutionPolicy Bypass -File scripts\package.ps1
# Tip: refresh the DB dump first -> scripts\db_dump.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$stage = Join-Path $env:TEMP ("dcpkg_" + (Get-Date -Format "yyyyMMddHHmmss"))
$zip = Join-Path $root "DofusCockpit-package.zip"
Remove-Item $zip -Force -ErrorAction SilentlyContinue

# Filtered copy to a staging dir (robocopy: /XD = dirs, /XF = files).
# data\live and dev .pcapng are excluded; data\db_backup.dump is kept.
robocopy $root $stage /E /NFL /NDL /NJH /NJS /NP `
    /XD "$root\.git" "$root\build" "$root\.idea" "$root\.claude" "$root\.agentbridge" "$root\.agent-work" "$root\.venv" "$root\venv" "$root\node_modules" "$root\data\live" "$root\data\details" ffdec_core ffdec_full ffdec_loader ffdec_pcode ffdec_pc2 __pycache__ `
    /XF *.pyc *.zip *.pcapng *.log "*_probe.py" | Out-Null
if ($LASTEXITCODE -ge 8) { Write-Error "robocopy failed (code $LASTEXITCODE)"; exit 1 }
Get-ChildItem -Path $stage -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

if (-not (Test-Path (Join-Path $stage "DofusCockpit.exe"))) { Write-Warning "DofusCockpit.exe missing - run scripts\build_exe.ps1 first." }
if (-not (Test-Path (Join-Path $stage "data\db_backup.dump"))) { Write-Warning "data\db_backup.dump missing - run scripts\db_dump.ps1 first (else the new PC re-seeds from the wiki)." }

Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -Force
Remove-Item $stage -Recurse -Force
Write-Host ("OK -> {0} ({1:N1} MB)" -f $zip, ((Get-Item $zip).Length / 1MB))
Write-Host "Copy this .zip to the other PC, unzip, then: powershell -ExecutionPolicy Bypass -File scripts\setup.ps1"
