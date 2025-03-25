"""
Versão simplificada do main.py para diagnosticar problemas.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Configurar logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Gerenciar ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialização
    logger.info("Iniciando aplicação simplificada")
    yield
    # Código de encerramento
    logger.info("Encerrando aplicação simplificada")

# Criar aplicação
app = FastAPI(
    title="CCONTROL-M Simplified",
    description="Versão simplificada do CCONTROL-M para diagnóstico",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de logging
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware para logging de requisições.
    """
    logger.debug(f"Recebida requisição: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"Enviada resposta: {response.status_code}")
    return response

# Endpoints básicos
@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "CCONTROL-M Simplified API"}

@app.get("/api/v1/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    return {"status": "ok"}

# Tentar importar componentes que podem estar causando problemas
try:
    # Testar importação do sistema de autenticação
    from app.dependencies import get_current_user
    
    @app.get("/api/v1/auth/test")
    async def auth_test():
        """Teste de importação do sistema de autenticação."""
        return {"status": "ok", "message": "Sistema de autenticação importado com sucesso"}
except ImportError as e:
    logger.error(f"Erro ao importar sistema de autenticação: {str(e)}")
    
    @app.get("/api/v1/auth/test")
    async def auth_test():
        return {"status": "error", "message": f"Erro ao importar: {str(e)}"}

# Tentar importar rotas comuns
try:
    # Tentar importar rota de empresa
    from app.routers.empresa_router import router as empresa_router
    
    # Incluir a rota se a importação teve sucesso
    app.include_router(empresa_router, prefix="/api/v1")
    
    @app.get("/api/v1/routes/empresa-test")
    async def empresa_routes_test():
        """Teste de importação das rotas de empresa."""
        return {"status": "ok", "message": "Rotas de empresa importadas com sucesso"}
except Exception as e:
    logger.error(f"Erro ao importar rotas de empresa: {str(e)}")
    
    @app.get("/api/v1/routes/empresa-test")
    async def empresa_routes_test():
        return {"status": "error", "message": f"Erro: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="debug") 