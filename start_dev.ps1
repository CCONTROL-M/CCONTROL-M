# Script PowerShell para iniciar o ambiente de desenvolvimento
Write-Host "Iniciando ambiente de desenvolvimento CCONTROL-M..." -ForegroundColor Green

# Verificar se já existem processos rodando nas portas 3000 e 8000
Write-Host "Verificando processos ativos nas portas 3000 e 8000..." -ForegroundColor Yellow

# Função para verificar e matar processos em uma porta específica
function Stop-ProcessOnPort {
    param (
        [int]$Port
    )
    
    Write-Host "Verificando processos na porta $Port..." -ForegroundColor Yellow
    
    # Tenta várias abordagens para garantir que a porta seja liberada
    try {
        # Abordagem 1: Usando netstat e taskkill
        $processInfo = netstat -ano | Select-String "[:.]$Port\s+.*LISTENING"
        if ($processInfo) {
            $processInfo | ForEach-Object {
                $line = $_ -split '\s+'
                $processId = $line | Select-Object -Last 1
                
                if ($processId -match '^\d+$') {
                    Write-Host "Encerrando processo (PID: $processId) na porta $Port..." -ForegroundColor Yellow
                    taskkill /PID $processId /F /T | Out-Null
                    Write-Host "Processo na porta $Port finalizado." -ForegroundColor Green
                }
            }
        }
        
        # Abordagem 2: Verificação adicional para garantir
        Start-Sleep -Seconds 1
        $checkAgain = netstat -ano | Select-String "[:.]$Port\s+.*LISTENING"
        if ($checkAgain) {
            Write-Host "Alguns processos ainda estão usando a porta $Port. Tentando novamente..." -ForegroundColor Red
            $checkAgain | ForEach-Object {
                $line = $_ -split '\s+'
                $processId = $line | Select-Object -Last 1
                
                if ($processId -match '^\d+$') {
                    Write-Host "Encerrando processo persistente (PID: $processId)..." -ForegroundColor Yellow
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                }
            }
        }
    }
    catch {
        Write-Host "Erro ao finalizar processos na porta $Port`: $_" -ForegroundColor Red
    }
    
    # Verifica se a porta foi liberada
    $portFree = -not (netstat -ano | Select-String "[:.]$Port\s+.*LISTENING")
    return $portFree
}

# Liberar portas
$port3000Free = Stop-ProcessOnPort -Port 3000
$port8000Free = Stop-ProcessOnPort -Port 8000

if (-not $port3000Free) {
    Write-Host "AVISO: Não foi possível liberar completamente a porta 3000!" -ForegroundColor Red
    Write-Host "O frontend pode não iniciar corretamente." -ForegroundColor Red
}

if (-not $port8000Free) {
    Write-Host "AVISO: Não foi possível liberar completamente a porta 8000!" -ForegroundColor Red
    Write-Host "O backend pode não iniciar corretamente." -ForegroundColor Red
}

# Criar diretório de logs se não existir
Write-Host "Verificando diretório de logs..." -ForegroundColor Yellow
try {
    if (-not (Test-Path "logs")) {
        Write-Host "Criando diretório de logs..." -ForegroundColor Gray
        New-Item -Path "logs" -ItemType Directory | Out-Null
        Write-Host "Diretório de logs criado com sucesso." -ForegroundColor Green
    }
} catch {
    Write-Host "Erro ao criar diretório de logs. Tentando continuar..." -ForegroundColor Red
}

# Definir títulos para as janelas
$backendTitle = "Backend CCONTROL-M"
$frontendTitle = "Frontend CCONTROL-M"

# Iniciar o backend em uma nova janela PowerShell
Write-Host "Iniciando backend..." -ForegroundColor Cyan
try {
    $backendScript = @"
    `$host.ui.RawUI.WindowTitle = '$backendTitle'
    cd '$PWD\backend'
    Write-Host 'Iniciando backend na porta 8000' -ForegroundColor Cyan
    uvicorn app.main:app --reload --port 8000 *> '..\logs\backend.log'
    if (`$LASTEXITCODE -ne 0) {
        Write-Host 'Falha ao iniciar o backend. Verifique se o Uvicorn está instalado.' -ForegroundColor Red
        Read-Host 'Pressione ENTER para sair'
    }
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript
} catch {
    Write-Host "Erro ao iniciar o backend: $_" -ForegroundColor Red
}

Write-Host "Aguardando inicialização do backend (5 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Iniciar o frontend em uma nova janela PowerShell
Write-Host "Iniciando frontend..." -ForegroundColor Cyan
try {
    $frontendScript = @"
    `$host.ui.RawUI.WindowTitle = '$frontendTitle'
    Set-Location '$PWD\frontend'
    Write-Host 'Iniciando frontend na porta 3000' -ForegroundColor Cyan
    # Usando & para chamar o comando npm diretamente no PowerShell
    & npm run dev *> '..\logs\frontend.log'
    if (`$LASTEXITCODE -ne 0) {
        Write-Host 'Falha ao iniciar o frontend. Verifique se o Node.js está instalado corretamente.' -ForegroundColor Red
        Read-Host 'Pressione ENTER para sair'
    }
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript
} catch {
    Write-Host "Erro ao iniciar o frontend: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Ambiente de desenvolvimento iniciado!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Docs API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se os servidores não iniciarem automaticamente, tente executar manualmente:" -ForegroundColor Yellow
Write-Host "- Backend: cd backend; uvicorn app.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host "- Frontend: cd frontend; npm run dev" -ForegroundColor Gray 