# Script PowerShell para iniciar o ambiente de desenvolvimento no Windows
Write-Host "Iniciando ambiente de desenvolvimento..." -ForegroundColor Green

# Definir o diretório atual como o diretório do script
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Adicionar o diretório atual ao PYTHONPATH
$env:PYTHONPATH = "$env:PYTHONPATH;$ScriptDir"

# Verificar se as variáveis de ambiente estão configuradas
if (-not (Test-Path .env)) {
    Write-Host "Arquivo .env não encontrado. Copiando de .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

# Iniciar o servidor
Write-Host "Iniciando servidor Uvicorn..." -ForegroundColor Green
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 