# Script para iniciar o CCONTROL-M
# Executa o backend e o frontend em janelas separadas do PowerShell

Write-Host "=== Iniciando CCONTROL-M ===" -ForegroundColor Green
Write-Host "Este script iniciará o backend e o frontend em janelas separadas." -ForegroundColor Yellow

# Função para verificar se um diretório existe
function Test-DirectoryExists($path) {
    if (-not (Test-Path $path -PathType Container)) {
        Write-Host "Erro: Diretório $path não encontrado!" -ForegroundColor Red
        Write-Host "Certifique-se de estar executando este script no diretório raiz do projeto." -ForegroundColor Red
        exit 1
    }
}

# Verificar se os diretórios frontend e backend existem
Test-DirectoryExists ".\frontend"
Test-DirectoryExists ".\backend"

# Caminho completo para o diretório atual
$currentDir = (Get-Location).Path

# Comando para o backend
$backendCmd = "cd '$currentDir\backend'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload"

# Comando para o frontend
$frontendCmd = "cd '$currentDir\frontend'; npm run dev"

# Iniciar backend em uma nova janela do PowerShell
Write-Host "Iniciando backend na porta 8002..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Aguardar um pouco para o backend iniciar
Write-Host "Aguardando o backend iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Iniciar frontend em uma nova janela do PowerShell
Write-Host "Iniciando frontend na porta 3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "=== Processo de inicialização concluído ===" -ForegroundColor Green
Write-Host "Backend disponível em: http://127.0.0.1:8002/docs" -ForegroundColor Magenta
Write-Host "Frontend disponível em: http://localhost:3000" -ForegroundColor Magenta
Write-Host "Para encerrar, feche as janelas do PowerShell ou pressione Ctrl+C em cada uma delas." -ForegroundColor Yellow 