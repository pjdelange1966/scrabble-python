# Eenmalige projectinstallatie. Uitvoeren vanuit de projectmap:
#   .\scripts\setup.ps1
# Als scripts geblokkeerd zijn:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
Write-Host "Klaar. Activeer later met: .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
