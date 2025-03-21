"""
Ponto de entrada principal da aplicação FastAPI para o backend do CCONTROL-M.

Este arquivo instancia a aplicação, configura middlewares e registra rotas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routers import usuarios, empresas, clientes, produtos
from app.routers.auth import router as auth_router

# Instância principal da aplicação
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua por domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas básicas de saúde
@app.get("/", tags=["Root"])
def read_root():
    return {"message": f"{settings.APP_NAME} backend is running."}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# Registro dos routers
app.include_router(auth_router)
app.include_router(usuarios.router)
app.include_router(empresas.router)
app.include_router(clientes.router)
app.include_router(produtos.router)

# Registro futuro de outros routers
# app.include_router(categorias.router) 