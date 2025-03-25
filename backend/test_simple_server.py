from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Iniciando servidor simples na porta 8002...")
    uvicorn.run(app, host="127.0.0.1", port=8002) 