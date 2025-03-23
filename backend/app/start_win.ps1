# Script PowerShell para iniciar o ambiente de desenvolvimento no Windows
# Para executar: powershell.exe -ExecutionPolicy Bypass -File .\start_win.ps1

Write-Host "Iniciando ambiente de desenvolvimento CCONTROL-M..." -ForegroundColor Green

# Definir o diretório atual como o diretório do script
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Adicionar o diretório atual ao PYTHONPATH
$env:PYTHONPATH = "$env:PYTHONPATH;$ScriptDir"

# Verificar se as variáveis de ambiente estão configuradas
if (-not (Test-Path .env)) {
    Write-Host "Arquivo .env não encontrado. Copiando de .env.example..." -ForegroundColor Yellow
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Host "Arquivo .env criado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Arquivo .env.example não encontrado. Verifique a instalação." -ForegroundColor Red
        exit 1
    }
}

# Verificar se o ambiente virtual Python está ativado
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Ambiente virtual Python não ativado. Verificando venv..." -ForegroundColor Yellow
    
    # Verificar se o venv existe
    if (Test-Path ..\venv) {
        Write-Host "Ativando ambiente virtual Python..." -ForegroundColor Green
        try {
            & ..\venv\Scripts\Activate.ps1
        } catch {
            Write-Host "Não foi possível ativar o ambiente virtual. Continuando sem ativação..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Ambiente virtual não encontrado. O aplicativo pode não funcionar corretamente." -ForegroundColor Yellow
    }
}

# Iniciar o servidor
Write-Host "Iniciando servidor Uvicorn..." -ForegroundColor Green
try {
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host "Erro ao iniciar o servidor: $_" -ForegroundColor Red
    exit 1
} 