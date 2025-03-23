# Script PowerShell para diagnóstico do ambiente CCONTROL-M
Write-Host "Iniciando diagnóstico do ambiente CCONTROL-M..." -ForegroundColor Green

# Verificar portas em uso
Write-Host "Verificando portas em uso..." -ForegroundColor Cyan
$port3000 = netstat -ano | findstr :3000
$port8000 = netstat -ano | findstr :8000

if ($port3000) {
    Write-Host "Porta 3000 (Frontend): EM USO" -ForegroundColor Green
    Write-Host $port3000
} else {
    Write-Host "Porta 3000 (Frontend): NÃO ESTÁ EM USO" -ForegroundColor Red
}

if ($port8000) {
    Write-Host "Porta 8000 (Backend): EM USO" -ForegroundColor Green
    Write-Host $port8000
} else {
    Write-Host "Porta 8000 (Backend): NÃO ESTÁ EM USO" -ForegroundColor Red
}

# Verificar se os arquivos de configuração existem
Write-Host "`nVerificando arquivos de configuração..." -ForegroundColor Cyan
$backendEnv = Test-Path "backend\.env"
$frontendConfig = Test-Path "frontend\vite.config.ts"

if ($backendEnv) {
    Write-Host "Arquivo backend\.env: ENCONTRADO" -ForegroundColor Green
} else {
    Write-Host "Arquivo backend\.env: NÃO ENCONTRADO" -ForegroundColor Red
    Write-Host "Recomendação: Copie backend\.env.example para backend\.env" -ForegroundColor Yellow
}

if ($frontendConfig) {
    Write-Host "Arquivo frontend\vite.config.ts: ENCONTRADO" -ForegroundColor Green
} else {
    Write-Host "Arquivo frontend\vite.config.ts: NÃO ENCONTRADO" -ForegroundColor Red
}

# Testar conexão com o backend
Write-Host "`nTestando conexão com o backend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/status" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "Conexão com backend: SUCESSO" -ForegroundColor Green
        Write-Host "Status API: $($response.Content)" -ForegroundColor Green
    }
} catch {
    Write-Host "Conexão com backend: FALHA" -ForegroundColor Red
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
}

# Verificar logs de erro recentes
Write-Host "`nVerificando logs de erro recentes..." -ForegroundColor Cyan
if (Test-Path "backend\logs\error.log") {
    Write-Host "Últimas 5 linhas do log de erro:" -ForegroundColor Yellow
    Get-Content "backend\logs\error.log" -Tail 5
} else {
    Write-Host "Arquivo de log de erro não encontrado" -ForegroundColor Yellow
}

# Verificar node_modules
Write-Host "`nVerificando dependências do projeto..." -ForegroundColor Cyan
$backendVenv = Test-Path "backend\venv"
$frontendNodeModules = Test-Path "frontend\node_modules"

if ($backendVenv) {
    Write-Host "Ambiente virtual Python: ENCONTRADO" -ForegroundColor Green
} else {
    Write-Host "Ambiente virtual Python: NÃO ENCONTRADO" -ForegroundColor Red
    Write-Host "Recomendação: Execute 'python -m venv venv' no diretório backend" -ForegroundColor Yellow
}

if ($frontendNodeModules) {
    Write-Host "Node Modules: ENCONTRADO" -ForegroundColor Green
} else {
    Write-Host "Node Modules: NÃO ENCONTRADO" -ForegroundColor Red
    Write-Host "Recomendação: Execute 'npm install' no diretório frontend" -ForegroundColor Yellow
}

# Verificar CORS no backend
Write-Host "`nVerificando configuração CORS..." -ForegroundColor Cyan
if (Test-Path "backend\app\middlewares\cors_middleware.py") {
    $corsConfig = Get-Content "backend\app\middlewares\cors_middleware.py" -Raw
    if ($corsConfig -match "allow_origins=\[\"".*?localhost:3000") {
        Write-Host "Configuração CORS para localhost:3000: ENCONTRADO" -ForegroundColor Green
    } else {
        Write-Host "Configuração CORS para localhost:3000: NÃO ENCONTRADO" -ForegroundColor Red
        Write-Host "Recomendação: Verifique se localhost:3000 está nas origens permitidas do CORS" -ForegroundColor Yellow
    }
} else {
    Write-Host "Arquivo de configuração CORS não encontrado" -ForegroundColor Red
}

# Recomendações
Write-Host "`nRECOMENDAÇÕES:" -ForegroundColor Cyan
Write-Host "1. Verifique se tanto o backend quanto o frontend estão rodando" -ForegroundColor White
Write-Host "2. Verifique se a URL da API no frontend está correta (deve ser: http://localhost:8000)" -ForegroundColor White
Write-Host "3. Certifique-se de que as origens CORS no backend permitem o frontend (localhost:3000)" -ForegroundColor White
Write-Host "4. Caso o problema persista, use o script 'start_dev.ps1' para reiniciar todo o ambiente" -ForegroundColor White
Write-Host "5. Verifique os logs do backend para identificar erros específicos" -ForegroundColor White

Write-Host "`nDiagnóstico concluído!" -ForegroundColor Green 