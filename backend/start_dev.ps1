Write-Host "Iniciando ambiente de desenvolvimento..." -ForegroundColor Green
Set-Location $PSScriptRoot
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 