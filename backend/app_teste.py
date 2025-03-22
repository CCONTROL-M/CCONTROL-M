"""Versão simplificada da aplicação para testes."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Importar configurações
from app.config.settings import settings

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
    uvicorn.run("app_teste:app", host="0.0.0.0", port=8000, reload=True) 