"""
Versão ultrassimplificada da API CCONTROL-M para diagnóstico.
"""
from fastapi import FastAPI

# Criar aplicação
app = FastAPI(
    title="CCONTROL-M Minimal",
    description="Versão mínima para diagnóstico",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "API funcional!"}

@app.get("/api/v1/health")
async def health():
    """Endpoint de saúde."""
    return {"status": "ok"}

@app.get("/docs")
async def docs_redirect():
    """Redirecionamento para a documentação."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

# Executar se chamado diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003) 