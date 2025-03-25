# Script para iniciar o ambiente de produção do CCONTROL-M via Docker
# Compatível com Windows PowerShell

Write-Host "🚀 Iniciando ambiente de PRODUÇÃO CCONTROL-M com Docker..." -ForegroundColor Cyan

# Verificar se o Docker está disponível
try {
    docker --version | Out-Null
    Write-Host "✅ Docker encontrado no sistema." -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker não encontrado! Certifique-se de que o Docker Desktop está instalado e em execução." -ForegroundColor Red
    exit 1
}

# Verificar se o arquivo .env.docker existe
if (-not (Test-Path ".env.docker")) {
    Write-Host "⚠️ Arquivo .env.docker não encontrado. Criando arquivo com valores padrão..." -ForegroundColor Yellow
    Copy-Item ".env" ".env.docker" -ErrorAction SilentlyContinue
    
    # Se mesmo assim não existir, criar um aviso
    if (-not (Test-Path ".env.docker")) {
        Write-Host "❌ Não foi possível criar o arquivo .env.docker. Verifique as permissões de diretório." -ForegroundColor Red
        exit 1
    }
}

# Criar pasta de logs se não existir
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "📁 Pasta logs/ criada para armazenar logs de produção." -ForegroundColor Green
}

# Parar containers existentes se houver
Write-Host "🔄 Parando containers existentes do CCONTROL-M..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml down 2>$null

# Construir e iniciar containers em modo destacado
Write-Host "🏗️ Construindo e iniciando containers Docker..." -ForegroundColor Cyan
docker-compose --env-file .env.docker -f docker-compose.yml up -d --build

# Verificar status dos containers
$containersRunning = $true
$maxRetries = 10
$retryCount = 0

Write-Host "⏳ Verificando status dos containers..." -ForegroundColor Yellow

while ($retryCount -lt $maxRetries) {
    $backendStatus = docker ps --filter "name=ccontrol-m-backend" --format "{{.Status}}"
    $frontendStatus = docker ps --filter "name=ccontrol-m-frontend" --format "{{.Status}}"

    if ($backendStatus -match "Up" -and $frontendStatus -match "Up") {
        $containersRunning = $true
        break
    }

    $containersRunning = $false
    $retryCount++
    Start-Sleep -Seconds 3
    Write-Host "⌛ Aguardando containers iniciarem ($retryCount/$maxRetries)..." -ForegroundColor Yellow
}

if (-not $containersRunning) {
    Write-Host "❌ Falha ao iniciar containers. Verifique os logs para mais informações:" -ForegroundColor Red
    Write-Host "   docker logs ccontrol-m-backend" -ForegroundColor Gray
    Write-Host "   docker logs ccontrol-m-frontend" -ForegroundColor Gray
    exit 1
}

# Exibir informações de acesso
Write-Host "`n🎉 Ambiente de PRODUÇÃO iniciado com sucesso!" -ForegroundColor Green
Write-Host "📊 Frontend: http://localhost" -ForegroundColor Cyan
Write-Host "🔌 Backend API: http://localhost:8002/api/v1" -ForegroundColor Cyan
Write-Host "📚 Documentação API: http://localhost:8002/docs" -ForegroundColor Cyan

Write-Host "`n💡 Para visualizar logs:" -ForegroundColor Magenta
Write-Host "   - Frontend: docker logs -f ccontrol-m-frontend" -ForegroundColor Gray
Write-Host "   - Backend: docker logs -f ccontrol-m-backend" -ForegroundColor Gray

Write-Host "`n⚠️ Para encerrar o ambiente:" -ForegroundColor Yellow
Write-Host "   docker-compose down" -ForegroundColor Gray 