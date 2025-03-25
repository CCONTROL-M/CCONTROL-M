import uvicorn

if __name__ == "__main__":
    print("Iniciando o servidor na porta 8002...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8002, reload=True) 