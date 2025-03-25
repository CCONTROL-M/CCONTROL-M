"""
Aplicação principal do sistema CCONTROL-M.

Este módulo configura o aplicativo FastAPI, incluindo rotas, middlewares e dependências.
"""

import logging
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time
import shutil
import uuid
import sys
import traceback
from fastapi import status, Query
from uuid import UUID

# Configuração de logging simplificada
from app.utils.logging_config import RequestIDFilter, setup_logging, log_with_context

# Configurar logging
setup_logging(debug=os.getenv("DEBUG", "False").lower() == "true")
logger = logging.getLogger(__name__)

# Importar o router principal da API
try:
    from app.routers import api_router
except ImportError as e:
    logger.error(f"Erro ao importar api_router: {str(e)}", extra={"request_id": "startup"})
    raise

# Importar configurações
try:
    from app.config.settings import settings
except ImportError as e:
    # Fallback para configurações básicas em caso de erro
    logger.error(f"Erro ao importar configurações: {str(e)}", extra={"request_id": "startup"})
    class DefaultSettings:
        PROJECT_NAME = "CCONTROL-M"
        APP_NAME = "CCONTROL-M"
        APP_VERSION = "1.0.0"
        APP_ENV = "development"
        CORS_ORIGINS = ["*"]
        CORS_METHODS = ["*"]
    settings = DefaultSettings()

# Gerenciar ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialização - executa antes de iniciar o servidor
    request_id = "startup"
    log_with_context(logger, "info", f"Iniciando aplicação em ambiente: {settings.APP_ENV}", request_id=request_id)
    
    # Criar diretório de uploads se não existir
    uploads_dir = getattr(settings, "UPLOAD_DIR", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    log_with_context(logger, "info", f"Iniciando aplicação {settings.APP_NAME} v{settings.APP_VERSION} no ambiente {settings.APP_ENV}", 
                request_id=request_id)
    
    yield
    # Código de encerramento - executa quando o servidor é desligado
    log_with_context(logger, "info", "Encerrando aplicação", request_id="shutdown")

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para o sistema CCONTROL-M: Controle Financeiro, Vendas e Gestão",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Tentar montar diretório de arquivos estáticos
try:
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Diretório de arquivos estáticos montado: {static_dir}", extra={"request_id": "startup"})
except Exception as e:
    logger.error(f"Erro ao montar diretório estático: {str(e)}", extra={"request_id": "startup"})

# Middleware para adicionar request_id às requisições
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """
    Middleware que adiciona um ID único a cada requisição.
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Iniciar processamento da requisição
    try:
        response = await call_next(request)
        
        # Adicionar o request_id ao cabeçalho de resposta para debugging
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        logger.error(f"Erro não tratado no request_id_middleware: {str(e)}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=500,
            content={"detail": "Ocorreu um erro interno. Por favor, tente novamente."}
        )

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
        logger.error(f"Erro não tratado: {str(e)}", extra={"request_id": request_id})
        
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
    start_time = time.time()
    
    logger.info(f"Recebida requisição: {request.method} {request.url.path}", 
               extra={"request_id": request_id, "method": request.method, "path": request.url.path})
    
    response = await call_next(request)
    
    # Calcular tempo de processamento
    process_time = time.time() - start_time
    logger.info(f"Enviada resposta: {response.status_code} em {process_time:.4f}s", 
                extra={"request_id": request_id, "status_code": response.status_code, "process_time": process_time})
    
    return response

# Configurar CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3010",
    "http://localhost:3011",
    "http://localhost:3012",
    "http://localhost:3013",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3010",
    "http://127.0.0.1:3011",
    "http://127.0.0.1:3012",
    "http://127.0.0.1:3013"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Middleware CORS configurado", extra={"request_id": "startup"})

# Endpoint para verificação de saúde da API (disponível sem autenticação)
@app.get("/api/v1/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def api_health_check():
    """Endpoint público para verificação de saúde da API (não requer autenticação)."""
    return {"status": "ok", "version": settings.APP_VERSION}

# Incluir o router principal da API com o prefixo apropriado
try:
    logger.info("Registrando router da API", extra={"request_id": "startup"})
    app.include_router(api_router, prefix=settings.API_PREFIX)
    logger.info("Router da API registrado com sucesso", extra={"request_id": "startup"})
except Exception as e:
    logger.error(f"Erro ao registrar router da API: {str(e)}", extra={"request_id": "startup"})
    raise

# Endpoint para verificação de saúde da API
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Rota para verificação de saúde da API."""
    return {"status": "ok", "version": settings.APP_VERSION}

# Rota de teste para lançamentos - apenas para debugging
@app.get("/api/v1/lancamentos/teste", tags=["Teste"])
async def teste_lancamentos(
    id_empresa: UUID = Query(..., description="ID da empresa")
):
    """Rota de teste para lançamentos financeiros."""
    from uuid import uuid4
    from app.schemas.lancamento import Lancamento
    from app.utils.pagination import paginate
    
    # MOCK data para teste
    lancamentos = [
        Lancamento(
            id=uuid4(),
            descricao=f"Lançamento de teste {i}",
            valor=100.0 * i,
            data_lancamento=f"2023-{i:02d}-01",
            data_pagamento=f"2023-{i:02d}-10" if i % 3 != 0 else None,
            tipo="RECEITA" if i % 2 == 0 else "DESPESA",
            status="PENDENTE" if i % 3 == 0 else ("PAGO" if i % 3 == 1 else "CANCELADO"),
            id_categoria=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            id_empresa=id_empresa
        )
        for i in range(1, 11)
    ]
    
    # Simular paginação
    total = len(lancamentos)
    page = 1
    page_size = 10
    
    # Usar a função paginate para padronizar a resposta
    return paginate(lancamentos, total, page, page_size)

# Endpoint para documentação Swagger
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Documentação Swagger UI customizada.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentação API",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

# Redirecionar raiz para documentação
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """
    Redireciona a raiz para a documentação da API.
    """
    return RedirectResponse(url="/docs")

# Mostrar informações sobre as rotas cadastradas
@app.on_event("startup")
async def startup_event():
    """Função executada na inicialização da aplicação."""
    logger.info(f"Iniciando a API {settings.PROJECT_NAME} versão {settings.APP_VERSION}")
    
    # Criar tabelas no banco de dados se não existirem
    if settings.CREATE_TABLES_ON_STARTUP:
        await create_tables()
    
    # Listar todas as rotas
    routes = []
    for route in app.routes:
        if isinstance(route, fastapi.routing.APIRoute):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": route.methods,
            })
    
    logger.info(f"Total de rotas: {len(routes)}")
    for route in routes:
        logger.info(f"Rota: {route['path']} - Métodos: {route['methods']}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 