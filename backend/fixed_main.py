"""
Versão corrigida do main.py do CCONTROL-M.
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from typing import Dict, Any, Optional
import uuid

# Configuração básica de logger que inclui um request_id padrão
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'no-request-id'
        return True

# Configurar formatação básica de logs
log_format = '%(asctime)s - %(levelname)s - [%(request_id)s] - %(name)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
)

# Adicionar filtro de request_id a todos os loggers
root_logger = logging.getLogger()
root_logger.addFilter(RequestIDFilter())

logger = logging.getLogger(__name__)

# Função auxiliar para logging com contexto
def log_with_context(logger, level, message, request_id=None, **kwargs):
    """
    Registra uma mensagem com um ID de requisição e dados adicionais.
    
    Args:
        logger: Logger para registrar a mensagem
        level: Nível do log (debug, info, warning, error, critical)
        message: Mensagem a ser registrada
        request_id: ID da requisição (opcional)
        **kwargs: Dados adicionais para incluir no contexto
    """
    if request_id is None:
        request_id = 'no-request-id'
    
    extra = {'request_id': request_id}
    extra.update(kwargs)
    
    if level == 'debug':
        logger.debug(message, extra=extra)
    elif level == 'info':
        logger.info(message, extra=extra)
    elif level == 'warning':
        logger.warning(message, extra=extra)
    elif level == 'error':
        logger.error(message, extra=extra)
    elif level == 'critical':
        logger.critical(message, extra=extra)
    else:
        logger.info(message, extra=extra)

# Gerenciar ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialização
    log_with_context(logger, 'info', "Iniciando aplicação CCONTROL-M", request_id='startup')
    
    # Criar diretório de uploads se não existir
    os.makedirs("uploads", exist_ok=True)
    
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    yield
    # Código de encerramento
    log_with_context(logger, 'info', "Encerrando aplicação CCONTROL-M", request_id='shutdown')

# Configurações da aplicação
APP_NAME = "CCONTROL-M"
APP_VERSION = "1.0.0"
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = APP_ENV == "development"

# Criar aplicação FastAPI
app = FastAPI(
    title=APP_NAME,
    description="API para o sistema CCONTROL-M: Controle Financeiro, Vendas e Gestão",
    version=APP_VERSION,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
    debug=DEBUG
)

# Configurar CORS
origins = ["*"] if APP_ENV == "development" else [
    "http://localhost",
    "http://localhost:3000",
    "https://ccontrol-m.com"
]

log_with_context(logger, 'info', f"CORS configurado em ambiente {APP_ENV}", request_id='startup')
log_with_context(logger, 'info', f"CORS origens permitidas: {origins}", request_id='startup')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para adicionar request_id às requisições
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """
    Middleware que adiciona um ID único a cada requisição.
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Iniciar processamento da requisição
    response = await call_next(request)
    
    # Adicionar o request_id ao cabeçalho de resposta para debugging
    response.headers["X-Request-ID"] = request_id
    
    return response

# Middleware de tratamento de exceções
@app.middleware("http")
async def exception_handling_middleware(request: Request, call_next):
    """
    Middleware para tratar exceções e garantir formato de resposta consistente.
    """
    try:
        return await call_next(request)
    except Exception as e:
        request_id = getattr(request.state, 'request_id', 'unknown')
        log_with_context(logger, 'error', f"Erro não tratado: {str(e)}", request_id=request_id)
        
        status_code = 500
        if isinstance(e, HTTPException):
            status_code = e.status_code
        
        return JSONResponse(
            status_code=status_code,
            content={"detail": "Ocorreu um erro interno. Por favor, tente novamente."}
        )

# Middleware de logging com request_id
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Middleware para logging de requisições.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    log_with_context(logger, 'info', f"Recebida requisição: {request.method} {request.url.path}", request_id=request_id)
    
    response = await call_next(request)
    
    log_with_context(logger, 'info', f"Enviada resposta: {response.status_code}", request_id=request_id)
    return response

# Montar diretório de arquivos estáticos
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
log_with_context(logger, 'info', f"Diretório de arquivos estáticos montado: {static_dir}", request_id='startup')

# Endpoints básicos
@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": f"Bem-vindo à API do {APP_NAME}!"}

@app.get("/api/v1/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    return {"status": "ok", "version": APP_VERSION, "environment": APP_ENV}

# Importar e incluir rotas
# Comentado para evitar erros enquanto diagnosticamos
# Descomentar cada rota ao confirmar que está funcionando

# # Rotas de autenticação
# try:
#     from app.routers.auth_router import router as auth_router
#     app.include_router(auth_router, prefix="/api/v1")
#     log_with_context(logger, 'info', "Rotas de autenticação registradas", request_id='startup')
# except Exception as e:
#     log_with_context(logger, 'error', f"Erro ao registrar rotas de autenticação: {str(e)}", request_id='startup')

# # Rotas de usuários
# try:
#     from app.routers.usuario_router import router as usuario_router
#     app.include_router(usuario_router, prefix="/api/v1")
#     log_with_context(logger, 'info', "Rotas de usuários registradas", request_id='startup')
# except Exception as e:
#     log_with_context(logger, 'error', f"Erro ao registrar rotas de usuários: {str(e)}", request_id='startup')

# Adicione mais rotas aqui conforme necessário
# Sempre dentro de blocos try-except para evitar que um erro em uma rota
# derrube toda a aplicação

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info") 