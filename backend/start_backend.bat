@echo off
echo Iniciando servidor backend em localhost:8000...
cd %~dp0
uvicorn app.main:app --reload --host 0.0.0.0 