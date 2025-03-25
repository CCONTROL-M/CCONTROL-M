@echo off
echo === Iniciando CCONTROL-M ===
echo.
echo Este script iniciara o backend e o frontend em janelas separadas.
echo.

REM Verificar se os diretorios existem
if not exist ".\frontend" (
    echo Erro: Diretorio frontend nao encontrado!
    echo Certifique-se de estar executando este script no diretorio raiz do projeto.
    exit /b 1
)

if not exist ".\backend" (
    echo Erro: Diretorio backend nao encontrado!
    echo Certifique-se de estar executando este script no diretorio raiz do projeto.
    exit /b 1
)

REM Iniciar backend em uma nova janela
echo Iniciando backend na porta 8002...
start cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload"

REM Aguardar um pouco para o backend iniciar
echo Aguardando o backend iniciar...
timeout /t 3 /nobreak > nul

REM Iniciar frontend em uma nova janela
echo Iniciando frontend na porta 3000...
start cmd /k "cd frontend && npm run dev"

echo.
echo === Processo de inicializacao concluido ===
echo Backend disponivel em: http://127.0.0.1:8002/docs
echo Frontend disponivel em: http://localhost:3000
echo Para encerrar, feche as janelas de comando ou pressione Ctrl+C em cada uma delas.

REM Abrir o navegador
timeout /t 2 /nobreak > nul
start http://localhost:3000 