from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import platform
import time
import os
import psutil
import datetime

from app.db.session import get_db
from app.config.settings import settings

router = APIRouter()

class HealthStatus(BaseModel):
    status: str
    uptime: float
    version: str
    environment: str
    database_connected: bool
    system_info: dict

@router.get("", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Verificar a saúde da aplicação.
    
    Verifica:
    - Conectividade com o banco de dados
    - Tempo de atividade
    - Informações do sistema
    - Ambiente atual
    """
    start_time = time.time()
    
    # Verificar conexão com o banco
    db_connected = True
    try:
        # Executar uma consulta simples para testar a conexão
        await db.execute("SELECT 1")
    except Exception:
        db_connected = False
    
    # Obter estatísticas do sistema
    system_info = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "cpu_usage": psutil.cpu_percent(interval=0.1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "process_memory": round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2),  # MB
        "current_time": datetime.datetime.now().isoformat(),
        "response_time_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    # Determinar o status com base nas verificações
    status_ok = db_connected
    
    response_data = {
        "status": "healthy" if status_ok else "unhealthy",
        "uptime": time.time() - psutil.Process(os.getpid()).create_time(),
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database_connected": db_connected,
        "system_info": system_info
    }
    
    status_code = status.HTTP_200_OK if status_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    ) 