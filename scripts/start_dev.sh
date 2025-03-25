#!/bin/bash
# Script para iniciar o servidor de desenvolvimento
cd backend
python -m uvicorn app.main:app --reload --port 8002

