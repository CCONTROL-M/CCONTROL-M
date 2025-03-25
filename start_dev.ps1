# Script para iniciar o ambiente de desenvolvimento do CCONTROL-M
# Compatível com o ambiente de desenvolvimento atual (Frontend: 3000, Backend: 8002)

Write-Host "🚀 Iniciando ambiente de desenvolvimento CCONTROL-M..." -ForegroundColor Cyan

# Definir URLs e portas
$FRONTEND_PORT = 3000
$BACKEND_URL = "http://127.0.0.1:8002"

# Criar pastas de logs se não existirem
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "📁 Pasta logs/ criada." -ForegroundColor Green
}

# Função para verificar se porta está em uso
function Test-PortInUse {
    param($port)
    
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("127.0.0.1", $port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Verificar se portas estão em uso e limpar se necessário
if (Test-PortInUse $FRONTEND_PORT) {
    Write-Host "⚠️ Porta $FRONTEND_PORT em uso. Tentando encerrar processo..." -ForegroundColor Yellow
    try {
        $processId = Get-NetTCPConnection -LocalPort $FRONTEND_PORT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
        if ($processId) {
            Stop-Process -Id $processId -Force
            Write-Host "✅ Processo na porta $FRONTEND_PORT encerrado." -ForegroundColor Green
        }
    }
    catch {
        Write-Host "❌ Não foi possível encerrar o processo na porta $FRONTEND_PORT." -ForegroundColor Red
    }
}

# Iniciar o frontend
Write-Host "🖥️ Iniciando frontend na porta $FRONTEND_PORT..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "frontend"
$frontendLog = Join-Path $PSScriptRoot "logs\frontend.log"

Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd $frontendPath && npm run dev > $frontendLog 2>&1" -WindowStyle Normal

# Verificar se o backend está acessível
Write-Host "🔍 Verificando conexão com backend em $BACKEND_URL..." -ForegroundColor Cyan
$backendAvailable = $false
$retryCount = 0
$maxRetries = 3

while (-not $backendAvailable -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "$BACKEND_URL/health" -Method GET -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendAvailable = $true
            Write-Host "✅ Backend disponível em $BACKEND_URL" -ForegroundColor Green
        }
    }
    catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "⚠️ Backend não disponível. Tentativa $retryCount de $maxRetries..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
        else {
            Write-Host "❌ Backend não está acessível em $BACKEND_URL" -ForegroundColor Red
            Write-Host "⚠️ Verifique se o backend está em execução na porta 8002" -ForegroundColor Yellow
        }
    }
}

# Exibir URLs de acesso
Write-Host "`n📋 Ambiente de desenvolvimento iniciado!" -ForegroundColor Green
Write-Host "📊 Frontend: http://localhost:$FRONTEND_PORT" -ForegroundColor Cyan
Write-Host "🔌 Backend API: $BACKEND_URL/api/v1" -ForegroundColor Cyan
Write-Host "📚 Documentação API: $BACKEND_URL/docs" -ForegroundColor Cyan
Write-Host "📝 Logs: ./logs/frontend.log" -ForegroundColor Cyan
Write-Host "`n⚠️ Para encerrar, feche os terminais ou pressione Ctrl+C em cada um deles." -ForegroundColor Yellow 