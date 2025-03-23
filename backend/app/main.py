from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
import os
import logging
import time
import shutil
from pathlib import Path

# Importar rotas
from app.routers import api_router

# Importar configurações
from app.config.settings import settings

# Importar configuração de logs
from app.utils.logging_config import get_logger, log_with_context

# Tentar importar configuração de middlewares
try:
    from app.middlewares.setup import configure_middlewares
except ImportError:
    from app.middlewares.cors_middleware import setup_cors_middleware
    from app.middlewares.rate_limiter import create_rate_limiter_middleware
    from app.middlewares.audit_middleware import create_audit_middleware
    from app.middlewares.validation_middleware import create_validation_middleware
    from app.middlewares.logging_middleware import RequestLoggingMiddleware
    from app.middlewares.security_middleware import create_security_middleware
    from app.middlewares.performance_middleware import PerformanceMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    
    def configure_middlewares(app: FastAPI) -> None:
        # Configurar middleware CORS
        setup_cors_middleware(app)
        
        # Adicionar middleware de segurança
        app.middleware("http")(create_security_middleware())
        
        # Adicionar middleware de logging
        app.add_middleware(RequestLoggingMiddleware)
        
        # Adicionar middleware de performance
        app.add_middleware(PerformanceMiddleware)
        
        # Adicionar middleware de limitação de taxa
        if settings.RATE_LIMIT_ENABLED:
            app.middleware("http")(create_rate_limiter_middleware())
        
        # Adicionar middleware de compressão Gzip
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Adicionar middleware de auditoria
        if settings.ENABLE_AUDIT_LOG:
            app.middleware("http")(create_audit_middleware())
        
        # Adicionar middleware de validação
        app.middleware("http")(create_validation_middleware())

# Importar manipuladores de exceção
from app.core.exception_handlers import configure_exception_handlers

# Tentar importar componentes de métricas
try:
    from app.config.metrics import get_metrics_prometheus, get_metrics_dict, reset_metrics
except ImportError:
    # Fallback para métricas
    def get_metrics_prometheus():
        return "# Métricas não disponíveis"
    
    def get_metrics_dict():
        return {"status": "metrics_not_available"}
    
    def reset_metrics():
        pass

# Configurar logger
logger = get_logger(__name__)

# Gerenciar estado do aplicativo durante inicialização e encerramento
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialização - executa antes de iniciar o servidor
    request_id = "startup"
    log_with_context(logger, "info", f"Iniciando aplicação em ambiente: {settings.APP_ENV}", request_id=request_id)
    
    # Criar diretório de uploads se não existir
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    logger.info(f"Iniciando aplicação {settings.APP_NAME} v{settings.APP_VERSION} no ambiente {settings.APP_ENV}", 
                extra={"request_id": request_id})
    
    yield
    # Código de encerramento - executa quando o servidor é desligado
    log_with_context(logger, "info", "Encerrando aplicação", request_id="shutdown")

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para o sistema CCONTROL-M: Controle Financeiro, Vendas e Gestão",
    version=settings.APP_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Montar diretório de arquivos estáticos
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
logger.info(f"Diretório de arquivos estáticos montado: {static_dir}")

# Configurar middlewares
configure_middlewares(app)

# Configurar manipuladores de exceção globais
configure_exception_handlers(app)

# Manipulador global de exceções
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    log_with_context(
        logger, 
        "error", 
        f"Erro não tratado: {str(exc)}", 
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"detail": "Erro interno do servidor."}),
    )

# Incluir rotas
app.include_router(api_router, prefix="/api/v1")

# Rota raiz
@app.get("/", include_in_schema=False)
async def root():
    """Rota raiz da aplicação - redireciona para a documentação."""
    return RedirectResponse(url="/docs")

# Rota de documentação personalizada
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Documentação Swagger UI personalizada."""
    return get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title=f"{settings.PROJECT_NAME} - Documentação da API",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
    )

# Rota de métricas Prometheus
@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Endpoint para métricas Prometheus."""
    return PlainTextResponse(get_metrics_prometheus())

# Rota de status da API
@app.get("/status", include_in_schema=False)
async def status_check():
    """Endpoint para verificação de status da API."""
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }

# Rota de métricas de performance
@app.get("/metrics/performance", include_in_schema=False)
async def performance_metrics():
    """Endpoint para métricas de performance internas."""
    return JSONResponse(content=get_metrics_dict())

if __name__ == "__main__":
    import uvicorn
    
    # Configurações específicas para execução direta
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 8000))
    reload = settings.APP_ENV == "development"
    
    log_with_context(
        logger, 
        "info", 
        f"Iniciando servidor em {host}:{port} (reload: {reload})",
        request_id="startup"
    )
    
    uvicorn.run("app.main:app", host=host, port=port, reload=reload) 