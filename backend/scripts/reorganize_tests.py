#!/usr/bin/env python
"""
Script para reorganizar a estrutura de testes do CCONTROL-M.

Este script move os arquivos de teste para a estrutura recomendada:
- tests/unit/schemas/
- tests/unit/services/
- tests/unit/repositories/
- tests/integration/api/
- tests/integration/db/
- tests/e2e/
- tests/fixtures/

Execução:
    python scripts/reorganize_tests.py
"""
import os
import shutil
import re
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
TESTS_DIR = BASE_DIR / "tests"
APP_TESTS_DIR = BASE_DIR / "app" / "tests"

# Mapeamento de tipos de testes para diretórios
TEST_MAPPING = {
    # Testes de schemas vão para unit/schemas
    r"test_.*_schema\.py$": "unit/schemas",
    r"test_validators.*\.py$": "unit/schemas",
    
    # Testes de serviços vão para unit/services
    r"test_.*_service\.py$": "unit/services",
    r"unit_test_.*_service\.py$": "unit/services",
    
    # Testes de repositórios vão para unit/repositories
    r"test_.*_repository\.py$": "unit/repositories",
    
    # Testes de API vão para integration/api
    r"test_.*_endpoints\.py$": "integration/api",
    r"test_.*_router\.py$": "integration/api",
    
    # Testes de DB vão para integration/db
    r"test_db_.*\.py$": "integration/db",
    
    # Fixtures vão para fixtures
    r"fixtures\.py$": "fixtures",
    r"conftest\.py$": "fixtures",
}

def create_directory_structure():
    """Cria a estrutura de diretórios recomendada."""
    directories = [
        "unit/schemas",
        "unit/services",
        "unit/repositories",
        "integration/api",
        "integration/db",
        "e2e",
        "fixtures"
    ]
    
    for directory in directories:
        os.makedirs(TESTS_DIR / directory, exist_ok=True)
    
    print("✅ Estrutura de diretórios criada com sucesso.")

def get_destination_directory(filename):
    """Determina o diretório de destino para um arquivo de teste."""
    for pattern, destination in TEST_MAPPING.items():
        if re.search(pattern, filename):
            return destination
    
    # Caso não seja encontrado um padrão específico, determinar com base no contexto
    if "api" in filename or "router" in filename:
        return "integration/api"
    elif "service" in filename:
        return "unit/services"
    elif "repository" in filename or "db" in filename:
        return "unit/repositories"
    else:
        # Casos não mapeados vão para raiz do diretório de testes
        return ""

def log_move(src, dest):
    """Registra a movimentação de um arquivo."""
    print(f"📦 Movendo {src} para {dest}")

def move_tests():
    """Move os arquivos de teste para a estrutura recomendada."""
    # Lista todos os arquivos de teste no diretório atual de testes
    test_files = []
    for root, _, files in os.walk(TESTS_DIR):
        for file in files:
            if file.endswith(".py") and "test_" in file:
                test_files.append(os.path.join(root, file))
    
    # Lista todos os arquivos de teste no diretório app/tests
    if APP_TESTS_DIR.exists():
        for root, _, files in os.walk(APP_TESTS_DIR):
            for file in files:
                if file.endswith(".py") and "test_" in file:
                    test_files.append(os.path.join(root, file))
    
    # Move cada arquivo para o diretório adequado
    moved_count = 0
    for test_file in test_files:
        filename = os.path.basename(test_file)
        
        # Ignorar arquivos já na estrutura correta
        if any(part in test_file for part in ["unit/", "integration/", "e2e/", "fixtures/"]):
            continue
        
        # Determinar destino
        destination_dir = get_destination_directory(filename)
        if not destination_dir:
            print(f"⚠️ Não foi possível determinar destino para {filename}, mantendo no lugar original.")
            continue
        
        # Criar caminho de destino completo
        destination = TESTS_DIR / destination_dir / filename
        
        # Criar diretório de destino se não existir
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        # Verificar se o arquivo já existe no destino
        if os.path.exists(destination):
            print(f"⚠️ Arquivo {filename} já existe em {destination_dir}, renomeando para {filename.replace('.py', '_old.py')}")
            destination = TESTS_DIR / destination_dir / filename.replace(".py", "_old.py")
        
        # Mover arquivo
        try:
            # Usar shutil.copy2 para preservar metadados
            shutil.copy2(test_file, destination)
            log_move(test_file, destination_dir)
            moved_count += 1
            
            # Não remover o original ainda, para evitar perda de dados
            # os.remove(test_file)
        except Exception as e:
            print(f"❌ Erro ao mover {filename}: {str(e)}")
    
    print(f"✅ {moved_count} arquivos de teste reorganizados.")

def create_readme():
    """Cria um arquivo README.md explicando a estrutura de testes."""
    readme_content = """# Estrutura de Testes - CCONTROL-M

Esta pasta contém os testes automatizados do sistema CCONTROL-M, organizados da seguinte forma:

## Estrutura de Diretórios

- **unit/**: Testes unitários
  - **schemas/**: Testes de validação de schemas e validadores
  - **services/**: Testes de lógica de negócio (serviços)
  - **repositories/**: Testes de acesso a dados (repositórios)

- **integration/**: Testes de integração
  - **api/**: Testes de integração da API (rotas e endpoints)
  - **db/**: Testes de integração com banco de dados

- **e2e/**: Testes end-to-end

- **fixtures/**: Dados de teste compartilhados

## Convenções

- Os nomes dos arquivos de teste devem seguir o padrão `test_*.py`
- Utilize fixtures para evitar duplicação de código de configuração
- Os testes unitários não devem acessar recursos externos (banco de dados, APIs)
- Os testes de integração podem acessar recursos externos controlados (banco de teste)

## Executando os Testes

```bash
# Executar todos os testes
pytest

# Executar apenas testes unitários
pytest tests/unit

# Executar testes com cobertura
pytest --cov=app --cov-report=html
```

## Dicas para Manutenção

1. Mantenha os testes independentes entre si
2. Use mocks quando apropriado para isolar o código em teste
3. Evite testes duplicados cobrindo o mesmo cenário
4. Documente casos de teste complexos com comentários claros
"""
    
    readme_path = TESTS_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✅ Arquivo README.md criado em {readme_path}")

def main():
    """Função principal do script."""
    print("🔧 Reorganizando estrutura de testes do CCONTROL-M...")
    
    # Criar estrutura de diretórios
    create_directory_structure()
    
    # Mover arquivos de teste
    move_tests()
    
    # Criar README
    create_readme()
    
    print("✅ Reorganização concluída!")
    print("⚠️ IMPORTANTE: Os arquivos originais foram mantidos. Após verificar que tudo está correto,")
    print("⚠️ você pode remover manualmente os arquivos duplicados.")

if __name__ == "__main__":
    main() 