@echo off
echo ================================
echo    INICIALIZANDO CCONTROL-M
echo ================================
echo.
echo Finalizando processos antigos...
taskkill /f /im python.exe /t 2>nul
taskkill /f /im node.exe /t 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Iniciando os servidores...
echo.

REM Verificando se o diretório logs existe
if not exist "logs" mkdir logs

REM Iniciando o backend em segundo plano
start /b cmd /c "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ..\logs\backend.log 2>&1"

echo Backend iniciado na porta 8000.
echo.

REM Aguardando um momento para o backend iniciar
timeout /t 3 /nobreak >nul

REM Iniciando o frontend em segundo plano
start /b cmd /c "cd frontend && npm run dev > ..\logs\frontend.log 2>&1"

echo Frontend iniciado na porta 3000.
echo.

echo ================================
echo    SISTEMA ONLINE!
echo ================================
echo.
echo Aplicação disponível em:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - Documentação API: http://localhost:8000/docs
echo.
echo Para encerrar os serviços digite: CTRL+C
echo.
echo Logs salvos em:
echo - Backend: logs\backend.log
echo - Frontend: logs\frontend.log
echo ================================

start http://localhost:3000

REM Manter o terminal aberto
cmd /k 