@echo off
setlocal enabledelayedexpansion

echo === Iniciando ambiente de desenvolvimento CCONTROL-M ===
echo.

REM Criar diretório de logs se não existir
if not exist "logs" mkdir logs

REM Verificar se o Python está disponível
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python não foi encontrado. Verifique se está instalado e no PATH do sistema.
    goto :error_exit
)

REM Verificar se o npm está disponível
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: npm não foi encontrado. Verifique se está instalado e no PATH do sistema.
    goto :error_exit
)

echo Verificando processos nas portas 3000 e 8000...

REM Função para verificar e liberar portas
call :check_port 3000
call :check_port 8000

REM Iniciar o backend
echo.
echo Iniciando o backend na porta 8000...
start cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && cd .. && uvicorn app.main:app --reload > logs\backend.log 2>&1"

REM Iniciar o frontend
echo.
echo Iniciando o frontend na porta 3000...
start cmd /k "cd frontend && npm install && npm run dev > ..\logs\frontend.log 2>&1"

echo.
echo Ambiente de desenvolvimento iniciado com sucesso!
echo.
echo --------------------------------------------------------
echo Para acessar a aplicação, abra os seguintes endereços:
echo.
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - Documentação da API: http://localhost:8000/docs
echo --------------------------------------------------------
echo.
echo Os logs estão sendo gravados em:
echo - Backend: logs\backend.log
echo - Frontend: logs\frontend.log
echo.
goto :eof

:check_port
setlocal
set "PORT=%~1"
set "MAX_ATTEMPTS=3"
set "ATTEMPTS=0"

:try_again
set /a "ATTEMPTS+=1"
echo Tentativa %ATTEMPTS% de %MAX_ATTEMPTS% para liberar a porta %PORT%...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT% "') do (
    if not "%%a"=="0" (
        echo Encerrando processo na porta %PORT% (PID: %%a)
        taskkill /F /PID %%a >nul 2>&1
    )
)

REM Verificar se a porta ainda está em uso
netstat -ano | findstr ":%PORT% " >nul
if not errorlevel 1 (
    if %ATTEMPTS% LSS %MAX_ATTEMPTS% (
        echo Porta %PORT% ainda está em uso. Tentando novamente...
        goto :try_again
    ) else (
        echo AVISO: Não foi possível liberar completamente a porta %PORT% após %MAX_ATTEMPTS% tentativas.
    )
)

endlocal
goto :eof

:error_exit
echo.
echo FALHA: O ambiente de desenvolvimento não pôde ser iniciado.
echo Verifique os erros acima e tente novamente.
exit /b 1 