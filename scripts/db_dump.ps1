# Dumps the DB (item dictionary + recipes + icons + bank + prices) into
# data\db_backup.dump -- copy it with the project to install on another PC
# WITHOUT re-downloading/re-seeding the dictionary.
# Usage (project root, containers running): powershell -File scripts\db_dump.ps1
#
# Note: we go through 'cmd /c' for the binary redirection (PowerShell would
# corrupt the stream by re-encoding it to UTF-16).
cmd /c "docker compose exec -T db pg_dump -U dofus -Fc dofus > data\db_backup.dump"
if ($LASTEXITCODE -ne 0 -or !(Test-Path data\db_backup.dump)) { Write-Error "pg_dump failed"; exit 1 }
Write-Host ("OK -> data\db_backup.dump ({0:N1} MB)" -f ((Get-Item data\db_backup.dump).Length / 1MB))
