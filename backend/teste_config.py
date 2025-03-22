"""Script para testar a configuração do banco de dados e criar as tabelas."""
import os
from pathlib import Path

# Garantir que o arquivo .env é encontrado
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    print(f"Arquivo .env encontrado em: {env_path}")
else:
    print(f"AVISO: Arquivo .env não encontrado em: {env_path}")

# Importar configurações
from app.config.settings import settings
print(f"Configurações carregadas: DATABASE_URL={settings.DATABASE_URL}")

# Testar conexão com banco de dados
from app.database import engine, create_all_tables, Base
print(f"Engine criada: {engine}")

try:
    # Tentar criar todas as tabelas
    create_all_tables()
    print("Tabelas criadas com sucesso!")
except Exception as e:
    print(f"Erro ao criar tabelas: {str(e)}")

print("Teste concluído!") 