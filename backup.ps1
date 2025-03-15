# backup.ps1
$date = Get-Date -Format "yyyy-MM-dd-HHmm"
$backupDir = ".\.backups"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

python manage.py dumpdata --exclude admin.logentry --exclude auth.permission --exclude silk --exclude contenttypes --indent 2 > "$backupDir\bak-$date.json"

Write-Host "Backup completed: $backupDir\$date.json"
