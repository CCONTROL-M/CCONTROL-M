from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import platform
import time
import os
import psutil
import datetime

from app.config.settings import settings

router = APIRouter()

@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Verificar a saúde da aplicação.
    
    Endpoint simples para verificar se a API está online.
    """
    return {"status": "ok", "version": settings.APP_VERSION} 