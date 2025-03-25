"""Script simplificado para testes."""

import os

if __name__ == "__main__":
    print("Verificando ambiente Python...")
    print(f"Diretório atual: {os.getcwd()}")
    print("Verificando schemas...")
    
    # Verificar se diretório schemas existe
    if os.path.exists("app/schemas"):
        print("Diretório app/schemas encontrado")
        schemas_files = os.listdir("app/schemas")
        print(f"Arquivos: {schemas_files}")
    else:
        print("Diretório app/schemas não encontrado")
    
    # Verificar se o arquivo lancamento_simples.py existe
    if os.path.exists("app/schemas/lancamento_simples.py"):
        print("Arquivo lancamento_simples.py encontrado")
        with open("app/schemas/lancamento_simples.py", "r") as f:
            first_line = f.readline().strip()
            print(f"Primeira linha: {first_line}")
    else:
        print("Arquivo lancamento_simples.py não encontrado")
    
    # Verificar routers
    if os.path.exists("app/routers"):
        print("Diretório app/routers encontrado")
        routers_files = os.listdir("app/routers")
        print(f"Arquivos: {routers_files}")
    else:
        print("Diretório app/routers não encontrado")
        
    print("Verificação concluída") 