# Restores data\db_backup.dump into the running 'db' container.
# Usage (project root): powershell -File scripts\db_restore.ps1
if (!(Test-Path data\db_backup.dump)) { Write-Error "data\db_backup.dump not found"; exit 1 }
cmd /c "docker compose exec -T db pg_restore -U dofus -d dofus --clean --if-exists --no-owner < data\db_backup.dump"
Write-Host "Restore done."
