param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,

    [string]$TargetDatabase = "ecommerce_restore_test",

    [string]$DbHost = "localhost",

    [int]$Port = 5432,

    [string]$Username = "postgres"
)

$ErrorActionPreference = "Stop"


# =========================================
# 1. Validate target database name
# =========================================

if ($TargetDatabase -notmatch '^[A-Za-z0-9_]+$') {
    throw "Invalid target database name."
}


# =========================================
# 2. Validate backup file
# =========================================

if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

$BackupFile = (Resolve-Path $BackupFile).Path


# =========================================
# 3. Check required PostgreSQL tools
# =========================================

$requiredCommands = @(
    "psql",
    "createdb",
    "pg_restore"
)

foreach ($command in $requiredCommands) {

    $foundCommand = Get-Command $command -ErrorAction SilentlyContinue

    if (-not $foundCommand) {
        throw "$command not found. Add PostgreSQL bin folder to PATH."
    }
}


# =========================================
# 4. Check whether target DB already exists
# =========================================

Write-Host ""
Write-Host "Checking target database..."

$checkDatabaseArgs = @(
    "--host=$DbHost",
    "--port=$Port",
    "--username=$Username",
    "--dbname=postgres",
    "--tuples-only",
    "--no-align",
    "--command=SELECT 1 FROM pg_database WHERE datname='$TargetDatabase';"
)

$existingDatabase = & psql @checkDatabaseArgs

if ($LASTEXITCODE -ne 0) {
    throw "Could not connect to PostgreSQL."
}

$existingDatabase = (
    $existingDatabase |
    Out-String
).Trim()


if ($existingDatabase -eq "1") {

    throw (
        "Target database '$TargetDatabase' already exists. " +
        "Use a different test database name."
    )
}


# =========================================
# 5. Create restore-test database
# =========================================

Write-Host ""
Write-Host "Creating restore-test database..."

$createDatabaseArgs = @(
    "--host=$DbHost",
    "--port=$Port",
    "--username=$Username",
    $TargetDatabase
)

& createdb @createDatabaseArgs

if ($LASTEXITCODE -ne 0) {
    throw "Could not create restore database."
}


# =========================================
# 6. Restore backup
# =========================================

Write-Host ""
Write-Host "Restoring backup..."

$restoreArgs = @(
    "--host=$DbHost",
    "--port=$Port",
    "--username=$Username",
    "--dbname=$TargetDatabase",
    "--no-owner",
    "--no-privileges",
    "--exit-on-error",
    $BackupFile
)

& pg_restore @restoreArgs

if ($LASTEXITCODE -ne 0) {
    throw "Restore failed."
}


# =========================================
# 7. Verify restored tables
# =========================================

Write-Host ""
Write-Host "Verifying restored database..."

$tableCountArgs = @(
    "--host=$DbHost",
    "--port=$Port",
    "--username=$Username",
    "--dbname=$TargetDatabase",
    "--tuples-only",
    "--no-align",
    "--command=SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
)

$tableCount = & psql @tableCountArgs

if ($LASTEXITCODE -ne 0) {
    throw "Restore verification failed."
}

$tableCount = (
    $tableCount |
    Out-String
).Trim()


if ([int]$tableCount -le 0) {
    throw "Restore completed but no public tables were found."
}


# =========================================
# 8. Verify Alembic revision
# =========================================

$alembicArgs = @(
    "--host=$DbHost",
    "--port=$Port",
    "--username=$Username",
    "--dbname=$TargetDatabase",
    "--tuples-only",
    "--no-align",
    "--command=SELECT version_num FROM alembic_version;"
)

$alembicVersion = & psql @alembicArgs

if ($LASTEXITCODE -ne 0) {
    throw "Could not verify Alembic revision."
}

$alembicVersion = (
    $alembicVersion |
    Out-String
).Trim()


# =========================================
# 9. Success
# =========================================

Write-Host ""
Write-Host "================================="
Write-Host "RESTORE SUCCESS"
Write-Host "================================="
Write-Host "Database: $TargetDatabase"
Write-Host "Public tables: $tableCount"
Write-Host "Alembic revision: $alembicVersion"