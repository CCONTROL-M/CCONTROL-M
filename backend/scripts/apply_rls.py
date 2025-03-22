"""Script para aplicar as configurações de Row-Level Security (RLS) no PostgreSQL/Supabase."""
import os
import sys
import logging
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Adicionar diretório pai ao path para importar configurações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config.settings import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def execute_sql_file(cursor, file_path):
    """
    Executa o conteúdo de um arquivo SQL.
    
    Args:
        cursor: Cursor de conexão com o banco de dados
        file_path: Caminho do arquivo SQL
    
    Returns:
        bool: True se executou com sucesso, False caso contrário
    """
    try:
        logger.info(f"Executando arquivo SQL: {file_path}")
        with open(file_path, "r", encoding="utf-8") as sql_file:
            sql_content = sql_file.read()
            cursor.execute(sql_content)
        return True
    except Exception as e:
        logger.error(f"Erro ao executar o arquivo SQL {file_path}: {str(e)}")
        return False


def apply_rls():
    """
    Aplica as configurações RLS no banco de dados Supabase.
    """
    conn = None
    try:
        # Conectar ao banco de dados usando a string de conexão do Supabase
        logger.info("Conectando ao banco de dados Supabase...")
        conn = psycopg2.connect(settings.DATABASE_URI)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Criar cursor
        cursor = conn.cursor()
        
        # Caminho para o diretório de migrações RLS
        rls_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "migrations", "rls")
        
        # Arquivo para ativar RLS
        rls_file = os.path.join(rls_dir, "01_enable_rls.sql")
        
        # Executar arquivo SQL
        if execute_sql_file(cursor, rls_file):
            logger.info("Row-Level Security (RLS) no Supabase ativado com sucesso!")
        else:
            logger.error("Falha ao ativar Row-Level Security (RLS) no Supabase")
        
        # Fechar cursor
        cursor.close()
    
    except Exception as e:
        logger.error(f"Erro ao aplicar RLS: {str(e)}")
    
    finally:
        # Fechar conexão
        if conn:
            conn.close()
            logger.info("Conexão fechada")


def disable_rls():
    """
    Desativa as configurações RLS no banco de dados Supabase.
    """
    conn = None
    try:
        # Conectar ao banco de dados
        logger.info("Conectando ao banco de dados Supabase...")
        conn = psycopg2.connect(settings.DATABASE_URI)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Criar cursor
        cursor = conn.cursor()
        
        # Caminho para o diretório de migrações RLS
        rls_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "migrations", "rls")
        
        # Arquivo para desativar RLS
        rls_file = os.path.join(rls_dir, "02_disable_rls.sql")
        
        # Executar arquivo SQL
        if execute_sql_file(cursor, rls_file):
            logger.info("Row-Level Security (RLS) no Supabase desativado com sucesso!")
            logger.warning("ATENÇÃO: O RLS foi desativado. Isso não é recomendado em produção!")
        else:
            logger.error("Falha ao desativar Row-Level Security (RLS) no Supabase")
        
        # Fechar cursor
        cursor.close()
    
    except Exception as e:
        logger.error(f"Erro ao desativar RLS: {str(e)}")
    
    finally:
        # Fechar conexão
        if conn:
            conn.close()
            logger.info("Conexão fechada")


if __name__ == "__main__":
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description="Gerenciar configurações de Row-Level Security (RLS) no Supabase")
    parser.add_argument("--disable", action="store_true", help="Desativar RLS ao invés de ativar")
    
    # Obter argumentos
    args = parser.parse_args()
    
    # Executar função conforme argumento
    if args.disable:
        response = input("ATENÇÃO: Desativar o RLS pode expor dados. Tem certeza? (sim/não): ")
        if response.lower() in ["sim", "s", "yes", "y"]:
            disable_rls()
        else:
            logger.info("Operação cancelada.")
    else:
        apply_rls() 