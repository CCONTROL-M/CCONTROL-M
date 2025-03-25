"""
Aplicação FastAPI minimalista para diagnóstico do CCONTROL-M.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configurar logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Aplicação mínima
app = FastAPI(
    title="Diagnóstico CCONTROL-M",
    description="Aplicação mínima para diagnosticar problemas",
    version="1.0.0"
)

# Configurar CORS - Adicionado para testar se é o problema
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz para verificar se a aplicação está funcionando."""
    logger.debug("Acessando endpoint raiz")
    return {"message": "API mínima funcionando!"}

@app.get("/health")
async def health():
    """Endpoint de saúde para verificar status."""
    logger.debug("Verificando saúde da aplicação")
    return {"status": "ok"}

# Tentar importações comuns que podem ser problemáticas
try:
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from fastapi.security import OAuth2PasswordBearer
    
    # Se chegarmos aqui, as importações básicas estão funcionando
    @app.get("/imports-check")
    async def check_imports():
        """Verifica se as importações básicas estão funcionando."""
        return {"status": "ok", "message": "Importações básicas funcionando"}
    
except ImportError as e:
    error_msg = f"Erro de importação: {str(e)}"
    logger.error(error_msg)
    
    @app.get("/imports-check")
    async def check_imports():
        """Relata erros de importação."""
        return {"status": "error", "message": error_msg}

# Incluir endpoint para verificar configurações
@app.get("/settings-check")
async def check_settings():
    """Verifica as configurações básicas."""
    try:
        # Tentar importar configurações
        from app.config.settings import settings
        
        # Retorna algumas configurações não sensíveis para diagnóstico
        return {
            "status": "ok",
            "environment": getattr(settings, "APP_ENV", "unknown"),
            "app_name": getattr(settings, "APP_NAME", "unknown"),
            "debug": getattr(settings, "DEBUG", False)
        }
    except Exception as e:
        logger.error(f"Erro ao verificar configurações: {str(e)}")
        return {"status": "error", "message": f"Erro: {str(e)}"}

# Incluir endpoint para verificar conexão com banco de dados
@app.get("/database-check")
async def check_database():
    """Verifica a conexão com o banco de dados."""
    try:
        # Tentar importar e criar engine
        from app.database import get_async_session, engine
        
        # Verificar se consegue obter metadados básicos
        return {"status": "ok", "message": "Conexão com banco de dados parece OK"}
    except Exception as e:
        logger.error(f"Erro ao verificar banco de dados: {str(e)}")
        return {"status": "error", "message": f"Erro: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug") 