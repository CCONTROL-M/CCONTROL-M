# Script para iniciar o servidor de desenvolvimento no Windows
cd .\backend
python -m uvicorn app.main:app --reload --port 8002 