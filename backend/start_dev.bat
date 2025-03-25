@echo off
echo Iniciando ambiente de desenvolvimento na porta 8002...
cd %~dp0
set PYTHONPATH=%PYTHONPATH%;%~dp0
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8002 