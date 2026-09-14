param(
    [string]$Database = "ecommerce_db",
    [string]$DbHost = "localhost",
    [int]$Port = 5432,
    [string]$Username = "postgres",
    [string]$BackupDirectory = "$PSScriptRoot\..\backups"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
    throw "pg_dump not found. Add PostgreSQL bin folder to PATH."
}

New-Item `
    -ItemType Directory `
    -Force `
    -Path $BackupDirectory `
    | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

$backupFile = Join-Path `
    $BackupDirectory `
    "${Database}_${timestamp}.backup"

Write-Host "Creating PostgreSQL backup..."

& pg_dump `
    --host=$DbHost `
    --port=$Port `
    --username=$Username `
    --format=custom `
    --no-owner `
    --file=$backupFile `
    $Database

if ($LASTEXITCODE -ne 0) {
    throw "Database backup failed."
}

if (-not (Test-Path $backupFile)) {
    throw "Backup file was not created."
}

$file = Get-Item $backupFile

if ($file.Length -le 0) {
    throw "Backup file is empty."
}

Write-Host ""
Write-Host "BACKUP SUCCESS"
Write-Host "File: $backupFile"
Write-Host "Size: $($file.Length) bytes"