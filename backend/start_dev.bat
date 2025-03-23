@echo off
echo Iniciando ambiente de desenvolvimento...
cd %~dp0
set PYTHONPATH=%PYTHONPATH%;%~dp0
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 