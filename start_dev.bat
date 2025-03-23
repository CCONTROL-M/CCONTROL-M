@echo off
REM Script para iniciar o ambiente de desenvolvimento CCONTROL-M
echo [32m Iniciando ambiente de desenvolvimento CCONTROL-M... [0m

REM Verificar se já existem processos rodando nas portas 3000 e 8000
echo [33m Verificando processos ativos nas portas 3000 e 8000... [0m

netstat -ano | findstr :3000 > nul
if %ERRORLEVEL% EQU 0 (
    FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :3000') DO (
        echo [33m Processo encontrado na porta 3000 (PID: %%P). Tentando finalizar... [0m
        taskkill /PID %%P /F > nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo [32m Processo na porta 3000 finalizado com sucesso. [0m
        ) else (
            echo [31m Aviso: Nao foi possivel finalizar o processo na porta 3000. [0m
        )
        goto :after_port_3000
    )
) else (
    echo [90m Nenhum processo encontrado na porta 3000. [0m
)
:after_port_3000

netstat -ano | findstr :8000 > nul
if %ERRORLEVEL% EQU 0 (
    FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :8000') DO (
        echo [33m Processo encontrado na porta 8000 (PID: %%P). Tentando finalizar... [0m
        taskkill /PID %%P /F > nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo [32m Processo na porta 8000 finalizado com sucesso. [0m
        ) else (
            echo [31m Aviso: Nao foi possivel finalizar o processo na porta 8000. [0m
        )
        goto :after_port_8000
    )
) else (
    echo [90m Nenhum processo encontrado na porta 8000. [0m
)
:after_port_8000

REM Criar diretório de logs se não existir
if not exist "logs" (
    echo [33m Criando diretorio de logs... [0m
    mkdir logs
    if ERRORLEVEL 1 (
        echo [31m Erro ao criar diretorio de logs. Tentando continuar... [0m
    ) else (
        echo [32m Diretorio de logs criado com sucesso. [0m
    )
)

REM Verificar se os executáveis necessários estão presentes
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31m ERRO: Python nao foi encontrado. Certifique-se de que o Python esta instalado e no PATH. [0m
    goto :error_exit
)

where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31m ERRO: Node.js nao foi encontrado. Certifique-se de que o Node.js esta instalado e no PATH. [0m
    goto :error_exit
)

where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31m ERRO: npm nao foi encontrado. Certifique-se de que o npm esta instalado e no PATH. [0m
    goto :error_exit
)

REM Iniciar o backend em uma nova janela CMD
echo [36m Iniciando backend... [0m
start "Backend CCONTROL-M" cmd /k "cd backend && echo [36m Iniciando backend na porta 8000 [0m && uvicorn app.main:app --reload --port 8000 > ..\logs\backend.log 2>&1 || echo [31m Falha ao iniciar o backend. Verifique se o Uvicorn esta instalado. [0m"

REM Aguardar inicialização do backend
echo [33m Aguardando inicializacao do backend (5 segundos)... [0m
timeout /t 5 /nobreak > nul

REM Iniciar o frontend em uma nova janela CMD
echo [36m Iniciando frontend... [0m
start "Frontend CCONTROL-M" cmd /k "cd frontend && echo [36m Iniciando frontend na porta 3000 [0m && npm run dev > ..\logs\frontend.log 2>&1 || echo [31m Falha ao iniciar o frontend. Verifique se o Node.js esta instalado corretamente. [0m"

echo.
echo [32m Ambiente de desenvolvimento iniciado! [0m
echo.
echo [36m Backend: http://localhost:8000 [0m
echo [36m Frontend: http://localhost:3000 [0m
echo [36m Docs API: http://localhost:8000/docs [0m
echo.
echo [33m Se os servidores nao iniciarem automaticamente, tente executar manualmente: [0m
echo [90m - Backend: cd backend ^&^& uvicorn app.main:app --reload --port 8000 [0m
echo [90m - Frontend: cd frontend ^&^& npm run dev [0m
echo.
echo [90m Os logs estao sendo salvos em: logs\backend.log e logs\frontend.log [0m
goto :eof

:error_exit
echo [31m ERRO: Falha ao iniciar o ambiente de desenvolvimento. Verifique os requisitos. [0m
pause 