@echo off
echo ================================
echo    DESLIGANDO CCONTROL-M
echo ================================
echo.
echo Finalizando processos...

REM Finalizar processos Node.js (frontend)
echo Encerrando Frontend...
taskkill /f /im node.exe /t 2>nul

REM Finalizar processos Python (backend)
echo Encerrando Backend...
taskkill /f /im python.exe /t 2>nul

echo.
echo ================================
echo    SISTEMA DESLIGADO!
echo ================================
echo.
echo Todos os serviços foram encerrados.
echo.

timeout /t 3 