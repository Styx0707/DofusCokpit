# First-time install on ANOTHER PC (Windows x64).
# Prerequisites: Docker Desktop + Wireshark installed, Docker Desktop RUNNING.
# Usage (from the copied project root):
#     powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
#
# Does everything: .env, capture folder, build+start containers, wait for DB,
# then RESTORE data\db_backup.dump if present, else SEED the dictionary from the
# wiki (network required, slower).

$ErrorActionPreference = "Stop"

if (!(Test-Path .env)) { Copy-Item .env.example .env; Write-Host "[ok] .env created" }
New-Item -ItemType Directory -Force -Path data\live | Out-Null

Write-Host "[..] docker compose up -d --build db api"
docker compose up -d --build db api

Write-Host "[..] waiting for DB (healthy)"
$ok = $false
for ($i = 0; $i -lt 40; $i++) {
    $h = docker inspect -f '{{.State.Health.Status}}' dofus-cockpit-db-1 2>$null
    if ($h -eq "healthy") { $ok = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $ok) { Write-Error "DB not healthy - is Docker Desktop running?"; exit 1 }

if (Test-Path data\db_backup.dump) {
    Write-Host "[..] restoring DB from data\db_backup.dump"
    cmd /c "docker compose exec -T db pg_restore -U dofus -d dofus --clean --if-exists --no-owner < data\db_backup.dump"
} else {
    Write-Host "[..] no db_backup.dump: seeding the dictionary from the wiki (network required)"
    if (!(Test-Path data\items_all.json)) {
        Invoke-WebRequest -UseBasicParsing -Uri "https://wiki.moon-bot.io/api/items.json" -OutFile data\items_all.json
    }
    $m = "-v `"${PWD}/data:/srv/data`" -v `"${PWD}/scripts:/srv/scripts`""
    cmd /c "docker compose run --rm $m api python -m scripts.seed_names"
    cmd /c "docker compose run --rm $m api python -m scripts.fetch_recipes"
    cmd /c "docker compose run --rm $m api python -m scripts.seed data/recipes_full.json"
}

Write-Host ""
Write-Host "[done] Ready -> http://localhost:8000/ui/  (or double-click DofusCockpit.exe)"
Write-Host "       Then start the capture (exe or dumpcap) and open your bank in game."
