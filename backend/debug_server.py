import os
import sys
import traceback
import importlib.util

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Checking imports...")

try:
    import uvicorn
    print("✅ uvicorn importado com sucesso")
except ImportError as e:
    print("❌ Erro importando uvicorn:", e)
    print("Tentando instalar uvicorn...")
    os.system("pip install uvicorn")
    try:
        import uvicorn
        print("✅ uvicorn instalado e importado com sucesso")
    except ImportError:
        print("❌ Falha ao instalar uvicorn")

try:
    import fastapi
    print("✅ fastapi importado com sucesso")
except ImportError as e:
    print("❌ Erro importando fastapi:", e)
    print("Tentando instalar fastapi...")
    os.system("pip install fastapi")
    try:
        import fastapi
        print("✅ fastapi instalado e importado com sucesso")
    except ImportError:
        print("❌ Falha ao instalar fastapi")

print("\nVerificando módulo app.main...")
try:
    # Tentar importar app.main
    spec = importlib.util.find_spec("app.main")
    if spec is None:
        print("❌ Módulo app.main não encontrado!")
    else:
        print("✅ Módulo app.main encontrado")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ app.main importado com sucesso")
        if hasattr(module, "app"):
            print("✅ app.main.app encontrado")
        else:
            print("❌ app.main.app não encontrado!")
except Exception as e:
    print("❌ Erro ao importar app.main:", e)
    traceback.print_exc()

print("\nIniciando o servidor...")
try:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8002, reload=True)
except Exception as e:
    print("❌ Erro ao iniciar o servidor:", e)
    traceback.print_exc() 