# Script PowerShell para iniciar o ambiente de desenvolvimento
Write-Host "Iniciando ambiente de desenvolvimento CCONTROL-M..." -ForegroundColor Green

# Verificar se já existem processos rodando nas portas 3000 e 8000
$checkPort3000 = netstat -ano | findstr :3000
$checkPort8000 = netstat -ano | findstr :8000

if ($checkPort3000) {
    Write-Host "Já existe processo rodando na porta 3000. Finalizando..." -ForegroundColor Yellow
    $pid3000 = $checkPort3000 -split '\s+' | Select-Object -Last 1
    taskkill /PID $pid3000 /F
}

if ($checkPort8000) {
    Write-Host "Já existe processo rodando na porta 8000. Finalizando..." -ForegroundColor Yellow
    $pid8000 = $checkPort8000 -split '\s+' | Select-Object -Last 1
    taskkill /PID $pid8000 /F
}

# Criar diretório de logs se não existir
if (-not (Test-Path "logs")) {
    New-Item -Path "logs" -ItemType Directory
}

# Iniciar o backend em uma nova janela PowerShell
Start-Process powershell -ArgumentList "-NoExit -Command cd '$PWD\backend'; Write-Host 'Iniciando backend na porta 8000' -ForegroundColor Cyan; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Write-Host "Aguardando inicialização do backend (5 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Iniciar o frontend em uma nova janela PowerShell
Start-Process powershell -ArgumentList "-NoExit -Command cd '$PWD\frontend'; Write-Host 'Iniciando frontend na porta 3000' -ForegroundColor Cyan; npm run dev"

Write-Host "Ambiente de desenvolvimento iniciado!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Docs API: http://localhost:8000/docs" -ForegroundColor Cyan 