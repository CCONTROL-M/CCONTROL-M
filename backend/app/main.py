from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager

# Importar rotas
from app.routers import usuarios, empresas, clientes, categorias, centro_custos, logs_sistema, vendas, lancamentos, formas_pagamento, contas_bancarias, fornecedores, produtos

# Importar configurações
from app.config.settings import settings

# Importar configuração de logs e middleware
from app.utils.logging_config import get_logger, log_with_context
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.performance_middleware import PerformanceMiddleware

# Importar monitor de agendamento
from app.scripts.schedule_monitors import start_scheduler_thread

# Configurar logger
logger = get_logger(__name__)

# Gerenciar estado do aplicativo durante inicialização e encerramento
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialização - executa antes de iniciar o servidor
    log_with_context(logger, "info", "Iniciando aplicação")
    yield
    # Código de encerramento - executa quando o servidor é desligado
    log_with_context(logger, "info", "Encerrando aplicação")

# Criar aplicação FastAPI
app = FastAPI(
    title="CCONTROL-M API",
    description="API do sistema CCONTROL-M para gerenciamento financeiro e controle empresarial",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middleware de logging
app.add_middleware(RequestLoggingMiddleware)

# Adicionar middleware de performance
app.add_middleware(PerformanceMiddleware)

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
app.include_router(usuarios.router, prefix="/api")
app.include_router(empresas.router, prefix="/api")
app.include_router(clientes.router, prefix="/api")
app.include_router(categorias.router, prefix="/api")
app.include_router(centro_custos.router, prefix="/api")
app.include_router(logs_sistema.router, prefix="/api")
app.include_router(vendas.router, prefix="/api")
app.include_router(lancamentos.router, prefix="/api")
app.include_router(formas_pagamento.router, prefix="/api")
app.include_router(contas_bancarias.router, prefix="/api")
app.include_router(fornecedores.router, prefix="/api")
app.include_router(produtos.router, prefix="/api")

# Rota raiz
@app.get("/", tags=["Root"])
async def root():
    log_with_context(logger, "info", "Acessando rota raiz")
    return {"message": "CCONTROL-M API - Sistema de Gerenciamento Financeiro e Controle Empresarial"}

# Armazenar a referência do scheduler thread
scheduler_thread = None

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint de verificação de saúde para verificar se a API está em execução.
    """
    logger.info("Health check executado")
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    """
    Evento executado na inicialização da aplicação.
    """
    global scheduler_thread
    
    logger.info("Aplicação iniciada")
    
    # Iniciar o agendador de monitoramento em uma thread separada
    try:
        scheduler_thread = start_scheduler_thread()
        logger.info("Agendador de monitoramento iniciado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao iniciar agendador de monitoramento: {str(e)}")
    
    # Registrar informações sobre o estado inicial do sistema
    logger.info("Sistema inicializado com monitoramento de performance ativo")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação.
    """
    # O scheduler thread é daemon, então será encerrado automaticamente
    logger.info("Aplicação encerrada")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 