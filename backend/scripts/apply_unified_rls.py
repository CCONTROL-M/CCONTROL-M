#!/usr/bin/env python
"""
Script para aplicar as políticas RLS unificadas ao banco de dados.
Este script lê o arquivo SQL unificado e o executa no banco de dados.
"""
import os
import sys
import logging
import argparse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Aplicar políticas RLS unificadas ao banco de dados.')
    parser.add_argument('--env-file', type=str, default='.env',
                        help='Arquivo .env com as variáveis de ambiente (padrão: .env)')
    parser.add_argument('--sql-file', type=str, default='migrations/rls/supabase_rls_unified.sql',
                        help='Arquivo SQL com as políticas RLS (padrão: migrations/rls/supabase_rls_unified.sql)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Executa em modo de simulação, sem aplicar mudanças')
    return parser.parse_args()

def get_database_url():
    """Obtém a URL do banco de dados a partir das variáveis de ambiente."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("Variável de ambiente DATABASE_URL não encontrada")
    return db_url

def read_sql_file(filepath):
    """Lê o arquivo SQL e retorna seu conteúdo."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Arquivo SQL não encontrado: {filepath}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro ao ler arquivo SQL: {e}")
        sys.exit(1)

def execute_sql(engine, sql, dry_run=False):
    """Executa o SQL no banco de dados."""
    if dry_run:
        logger.info("MODO DE SIMULAÇÃO: SQL não será executado")
        logger.info(f"SQL que seria executado:\n{sql}")
        return
    
    # Dividir o SQL em declarações individuais
    # Esta é uma abordagem simples, pode precisar ser ajustada para casos mais complexos
    statements = sql.split(';')
    statements = [stmt.strip() for stmt in statements if stmt.strip()]
    
    with engine.connect() as conn:
        # Iniciar uma transação
        with conn.begin():
            for i, stmt in enumerate(statements, 1):
                try:
                    # Adicionar ponto e vírgula de volta para a execução
                    conn.execute(text(stmt + ';'))
                    logger.info(f"Executada declaração {i}/{len(statements)}")
                except Exception as e:
                    logger.error(f"Erro ao executar declaração {i}: {e}")
                    logger.error(f"SQL com erro: {stmt}")
                    # Não interromper em caso de erro, continuar com as próximas declarações
                    continue

def main():
    """Função principal."""
    args = parse_args()
    
    # Carregar arquivo .env específico se fornecido
    if args.env_file != '.env':
        load_dotenv(args.env_file)
    
    try:
        # Obter URL do banco de dados
        db_url = get_database_url()
        
        # Criar engine do SQLAlchemy
        engine = create_engine(db_url)
        
        # Ler arquivo SQL
        sql_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), args.sql_file)
        logger.info(f"Lendo arquivo SQL: {sql_path}")
        sql = read_sql_file(sql_path)
        
        # Executar SQL
        logger.info(f"Aplicando políticas RLS ao banco de dados{' (simulação)' if args.dry_run else ''}")
        execute_sql(engine, sql, args.dry_run)
        
        if not args.dry_run:
            logger.info("Políticas RLS aplicadas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao aplicar políticas RLS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 