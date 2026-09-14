$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path `
    -Parent `
    $PSScriptRoot

$Backend = Join-Path `
    $ProjectRoot `
    "backend"

$Python = Join-Path `
    $Backend `
    ".venv\Scripts\python.exe"


if (-not (Test-Path $Python)) {
    throw "Backend virtual environment Python not found."
}


Write-Host ""
Write-Host "================================="
Write-Host "PHASE 20 FULL REGRESSION"
Write-Host "================================="


Push-Location $Backend

try {

    Write-Host ""
    Write-Host "Checking Alembic revision..."

    & $Python -m alembic current

    if ($LASTEXITCODE -ne 0) {
        throw "Alembic current check failed."
    }


    Write-Host ""
    Write-Host "Running Phase 20 suite..."

    & $Python -m tests.phase20_full_regression

    if ($LASTEXITCODE -ne 0) {
        throw "Phase 20 regression failed."
    }


    Write-Host ""
    Write-Host "================================="
    Write-Host "PHASE 20 PASSED"
    Write-Host "================================="

}
finally {

    Pop-Location
}