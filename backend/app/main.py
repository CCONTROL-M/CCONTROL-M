from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import os
import logging
import time
from fastapi.middleware.gzip import GZipMiddleware

# Importar rotas
from app.routers import api_router

# Importar configurações
from app.config.settings import settings

# Importar configuração de logs
from app.utils.logging_config import get_logger, log_with_context

# Importar middlewares
from app.middlewares.cors_middleware import setup_cors_middleware
from app.middlewares.rate_limiter import create_rate_limiter_middleware
from app.middlewares.audit_middleware import create_audit_middleware
from app.middlewares.validation_middleware import create_validation_middleware
from app.middlewares.tenant_middleware import TenantMiddleware
from app.middlewares.performance_middleware import PerformanceMiddleware
from app.middlewares.logging_middleware import RequestLoggingMiddleware
from app.middlewares.https_redirect_middleware import HTTPSRedirectMiddleware
from app.middlewares.security_middleware import create_security_middleware

# Importar dependências
from app.db.session import create_db_and_tables

# Importar monitor de agendamento
from app.scripts.schedule_monitors import start_scheduler_thread

# Configurar logger
logger = get_logger(__name__)

# Gerenciar estado do aplicativo durante inicialização e encerramento
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialização - executa antes de iniciar o servidor
    log_with_context(logger, "info", f"Iniciando aplicação em ambiente: {settings.APP_ENV}")
    
    # Inicialização: criar tabelas no banco de dados se não existirem
    await create_db_and_tables()
    
    # Criar diretório de uploads se não existir
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    logger.info(f"Iniciando aplicação {settings.APP_NAME} v{settings.APP_VERSION} no ambiente {settings.APP_ENV}")
    
    yield
    # Código de encerramento - executa quando o servidor é desligado
    log_with_context(logger, "info", "Encerrando aplicação")

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

# Configurar middleware CORS (com configurações seguras)
setup_cors_middleware(app)

# Adicionar middleware de segurança integrado
app.middleware("http")(create_security_middleware())
logger.info("Middleware de segurança integrado ativado")

# Redirecionar HTTP para HTTPS em produção
if os.getenv("ENABLE_HTTPS_REDIRECT", "False").lower() == "true" and settings.APP_ENV == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    logger.info("Redirecionamento HTTP para HTTPS habilitado")

# Adicionar middleware de multi-tenancy
app.add_middleware(TenantMiddleware)
logger.info("Middleware de multi-tenancy ativado")

# Adicionar middleware de logging
app.add_middleware(RequestLoggingMiddleware)
logger.info("Middleware de logging ativado")

# Adicionar middleware de performance
app.add_middleware(PerformanceMiddleware)
logger.info("Middleware de performance ativado")

# Adicionar middleware de limitação de taxa se habilitado
if settings.RATE_LIMIT_ENABLED:
    app.middleware("http")(create_rate_limiter_middleware())
    logger.info(f"Middleware de limitação de taxa ativado: {settings.RATE_LIMIT_REQUESTS} requisições por {settings.RATE_LIMIT_WINDOW}s")

# Adicionar middleware de compressão Gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)
logger.info("Middleware de compressão Gzip ativado")

# Adicionar middleware de auditoria se habilitado
if settings.ENABLE_AUDIT_LOG:
    app.middleware("http")(create_audit_middleware())
    logger.info("Middleware de auditoria ativado")

# Adicionar middleware de validação e segurança
app.middleware("http")(create_validation_middleware())
logger.info("Middleware de validação e segurança ativado")

# Manipulador global de exceções
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log_with_context(
        logger, 
        "error", 
        f"Erro não tratado: {str(exc)}", 
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
    """Rota raiz da aplicação."""
    return {
        "message": f"Bem-vindo à API do {settings.PROJECT_NAME}", 
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }

# Armazenar a referência do scheduler thread
scheduler_thread = None

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint de verificação de saúde para verificar se a API está em execução.
    """
    return {
        "status": "ok", 
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }

@app.on_event("startup")
async def startup_event():
    """
    Evento executado na inicialização da aplicação.
    """
    global scheduler_thread
    
    logger.info(f"Aplicação iniciada em ambiente: {settings.APP_ENV}")
    
    # Iniciar o agendador de monitoramento em uma thread separada
    try:
        if settings.ENABLE_MONITORING or settings.APP_ENV == "production":
            scheduler_thread = start_scheduler_thread()
            logger.info("Agendador de monitoramento iniciado com sucesso")
        else:
            logger.info("Monitoramento desativado por configuração")
    except Exception as e:
        logger.error(f"Erro ao iniciar agendador de monitoramento: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação.
    """
    # O scheduler thread é daemon, então será encerrado automaticamente
    logger.info("Aplicação encerrada")

@app.get("/api/v1/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Rota para a documentação Swagger com estilo customizado."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - Documentação API",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.5.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.5.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

def custom_openapi():
    """Personalização da documentação OpenAPI."""
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.APP_VERSION,
        description="""
# CCONTROL-M: Sistema de Gestão Empresarial

Sistema modular para controle financeiro, vendas e gestão empresarial, com suporte a multi-locação.

## Módulos Principais

### Administrativo
- Usuários e permissões
- Empresas (multi-tenant)
- Logs do sistema

### Financeiro
- Lançamentos (receitas e despesas)
- Contas bancárias
- Categorias
- Centros de custo
- Formas de pagamento

### Vendas
- Clientes
- Vendas
- Parcelas
- Recebimentos

### Suprimentos
- Fornecedores
- Compras
- Pagamentos
        """,
        routes=app.routes,
    )
    
    # Adicionar tags com descrições detalhadas
    openapi_schema["tags"] = [
        {
            "name": "Autenticação",
            "description": "Operações de autenticação e autorização"
        },
        {
            "name": "Usuários",
            "description": "Gerenciamento de usuários, perfis e permissões"
        },
        {
            "name": "Empresas",
            "description": "Gerenciamento de empresas e configurações multi-tenant"
        },
        {
            "name": "Clientes",
            "description": "Cadastro e gestão de clientes"
        },
        {
            "name": "Fornecedores",
            "description": "Cadastro e gestão de fornecedores"
        },
        {
            "name": "Centros de Custo",
            "description": "Controle de centros de custo para classificação de lançamentos"
        },
        {
            "name": "Categorias",
            "description": "Categorias para classificação de lançamentos financeiros"
        },
        {
            "name": "Contas Bancárias",
            "description": "Gerenciamento de contas bancárias, caixa e carteiras"
        },
        {
            "name": "Formas de Pagamento",
            "description": "Gerenciamento de formas de pagamento para vendas e compras"
        },
        {
            "name": "Lançamentos",
            "description": "Registro e controle de lançamentos financeiros (receitas e despesas)"
        },
        {
            "name": "Vendas",
            "description": "Registro e gestão de vendas"
        },
        {
            "name": "Parcelas",
            "description": "Controle de parcelas de vendas e pagamentos"
        },
        {
            "name": "Relatórios",
            "description": "Relatórios e análises financeiras"
        },
        {
            "name": "Dashboard",
            "description": "Painéis e indicadores de desempenho"
        },
        {
            "name": "Logs",
            "description": "Registro de atividades e auditoria do sistema"
        },
        {
            "name": "Health",
            "description": "Verificação de saúde da aplicação"
        }
    ]
    
    # Adicionar componentes de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Entre com seu token JWT"
        }
    }
    
    # Aplicar segurança global
    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    
    # Configurações específicas para execução direta
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 8000))
    reload = settings.APP_ENV == "development"
    
    log_with_context(
        logger, 
        "info", 
        f"Iniciando servidor em {host}:{port} (reload: {reload})"
    )
    
    uvicorn.run("app.main:app", host=host, port=port, reload=reload) 