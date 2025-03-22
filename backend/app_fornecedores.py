"""Versão simplificada da aplicação para testar o router de fornecedores."""
from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer

# Importar configurações
from app.config.settings import settings

# Importar o banco de dados e criação de tabelas
from app.database import engine, create_all_tables, Base

# Token e autenticação simulados para teste
from app.dependencies import get_current_user as get_current_active_user

# Importar o router de fornecedores
from app.routers.fornecedores import router as fornecedores_router

# Criar tabelas no SQLite
create_all_tables()

# Configuração básica da aplicação
app = FastAPI(
    title=settings.APP_NAME,
    description="API para o sistema CCONTROL-M (versão de teste)",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir o router de fornecedores
app.include_router(fornecedores_router, prefix="/api")

# Rotas simples para teste
@app.get("/", include_in_schema=False)
async def root():
    """Rota raiz da aplicação."""
    return {"message": f"Bem-vindo à API do {settings.APP_NAME}", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_fornecedores:app", host="0.0.0.0", port=8000, reload=True) 