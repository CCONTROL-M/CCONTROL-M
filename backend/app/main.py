from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Importar rotas
from app.routers import usuarios, empresas, clientes, categorias, centro_custos, logs_sistema, vendas, parcelas, lancamentos, formas_pagamento, contas_bancarias, fornecedores, produtos

# Importar configurações
from app.config.settings import settings

# Importar configuração de logs e middleware
from app.utils.logging_config import get_logger, log_with_context
from app.middlewares.logging_middleware import RequestLoggingMiddleware
from app.middlewares.performance_middleware import PerformanceMiddleware
from app.middlewares.tenant_middleware import TenantMiddleware

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
    title=settings.PROJECT_NAME,
    description="API para o sistema CCONTROL-M: Controle Financeiro, Vendas e Gestão",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middleware de multi-tenancy
app.add_middleware(TenantMiddleware)

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
@app.get("/", include_in_schema=False)
async def root():
    """Rota raiz da aplicação."""
    return {"message": f"Bem-vindo à API do {settings.PROJECT_NAME}", "version": "1.0.0"}

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
        version="1.0.0",
        description="""
# Sistema CCONTROL-M: Controle Financeiro, Vendas e Gestão
        
O CCONTROL-M é um sistema completo para controle financeiro, gestão de vendas e administração
empresarial, desenvolvido com arquitetura multi-tenant para suporte a múltiplas empresas.

## Principais recursos

* **Multi-tenancy**: Separação completa de dados por empresa
* **Controle Financeiro**: Lançamentos, contas bancárias, categorias, centros de custo
* **Gestão de Vendas**: Cadastro de clientes, produtos, vendas e parcelas
* **Gestão de Fornecedores**: Cadastro, avaliação e transações
* **Administração**: Controle de usuários, permissões e empresas
* **Relatórios e Dashboards**: Visualização de dados e indicadores

## Módulos principais

### Gestão de Empresas e Usuários
- Cadastro e gerenciamento de empresas
- Controle de usuários e permissões
- Logs de atividades

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
            "name": "auth",
            "description": "Operações de autenticação e autorização"
        },
        {
            "name": "empresa",
            "description": "Gerenciamento de empresas e configurações multi-tenant"
        },
        {
            "name": "usuario",
            "description": "Gerenciamento de usuários, perfis e permissões"
        },
        {
            "name": "cliente",
            "description": "Cadastro e gestão de clientes"
        },
        {
            "name": "fornecedor",
            "description": "Cadastro e gestão de fornecedores"
        },
        {
            "name": "centro_custo",
            "description": "Controle de centros de custo para classificação de lançamentos"
        },
        {
            "name": "categoria",
            "description": "Categorias para classificação de lançamentos financeiros"
        },
        {
            "name": "conta_bancaria",
            "description": "Gerenciamento de contas bancárias, caixa e carteiras"
        },
        {
            "name": "forma_pagamento",
            "description": "Gerenciamento de formas de pagamento para vendas e compras"
        },
        {
            "name": "lancamento",
            "description": "Registro e controle de lançamentos financeiros (receitas e despesas)"
        },
        {
            "name": "venda",
            "description": "Registro e gestão de vendas"
        },
        {
            "name": "parcela",
            "description": "Controle de parcelas de vendas e pagamentos"
        },
        {
            "name": "relatorio",
            "description": "Relatórios e análises financeiras"
        },
        {
            "name": "dashboard",
            "description": "Painéis e indicadores de desempenho"
        },
        {
            "name": "log",
            "description": "Registro de atividades e auditoria do sistema"
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
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 