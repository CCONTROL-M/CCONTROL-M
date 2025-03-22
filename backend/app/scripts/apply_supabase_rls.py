#!/usr/bin/env python
"""
Script para aplicar as regras de Row Level Security (RLS) no Supabase
para o sistema CCONTROL-M.

Requer:
    - Acesso administrativo ao banco de dados Supabase
    - Variáveis de ambiente configuradas com credenciais
"""
import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

import psycopg2
from psycopg2 import sql

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/supabase_rls.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_connection(db_params):
    """Cria uma conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        logger.info("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        sys.exit(1)

def execute_sql_file(conn, sql_file_path):
    """Executa um arquivo SQL no banco de dados."""
    try:
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            
        # Dividir o script em comandos individuais
        sql_commands = sql_script.split(';')
        
        with conn.cursor() as cursor:
            for command in sql_commands:
                command = command.strip()
                if command:
                    logger.info(f"Executando comando: {command[:50]}...")
                    cursor.execute(command)
                    logger.info("Comando executado com sucesso.")
        
        logger.info(f"Arquivo SQL {sql_file_path} executado com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro ao executar o arquivo SQL: {e}")
        return False

def check_table_exists(conn, table_name):
    """Verifica se uma tabela existe no banco de dados."""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s);",
                (table_name,)
            )
            return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Erro ao verificar existência da tabela {table_name}: {e}")
        return False

def check_rls_enabled(conn, table_name):
    """Verifica se RLS está habilitado para uma tabela."""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT relrowsecurity FROM pg_class WHERE relname = %s;",
                (table_name,)
            )
            result = cursor.fetchone()
            return result[0] if result else False
    except Exception as e:
        logger.error(f"Erro ao verificar RLS para tabela {table_name}: {e}")
        return False

def main():
    """Função principal para aplicar as regras RLS."""
    parser = argparse.ArgumentParser(description='Aplicar regras RLS no Supabase')
    parser.add_argument('--env', default='.env.prod', help='Arquivo de variáveis de ambiente')
    parser.add_argument('--sql', default='scripts/supabase_rls.sql', help='Arquivo SQL com as regras RLS')
    args = parser.parse_args()
    
    # Verificar existência do arquivo SQL
    sql_file_path = Path(args.sql)
    if not sql_file_path.exists():
        logger.error(f"Arquivo SQL não encontrado: {sql_file_path}")
        sys.exit(1)
    
    # Carregar variáveis de ambiente
    env_file = Path(args.env)
    if not env_file.exists():
        logger.error(f"Arquivo de ambiente não encontrado: {env_file}")
        sys.exit(1)
    
    load_dotenv(env_file)
    
    # Verificar se as variáveis necessárias estão definidas
    required_vars = ["SUPABASE_URL", "SUPABASE_DB_HOST", "SUPABASE_DB_PORT", 
                     "SUPABASE_DB_NAME", "SUPABASE_DB_USER", "SUPABASE_DB_PASSWORD"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Configurar parâmetros de conexão
    db_params = {
        "host": os.getenv("SUPABASE_DB_HOST"),
        "port": os.getenv("SUPABASE_DB_PORT"),
        "database": os.getenv("SUPABASE_DB_NAME"),
        "user": os.getenv("SUPABASE_DB_USER"),
        "password": os.getenv("SUPABASE_DB_PASSWORD")
    }
    
    # Criar diretório de logs se não existir
    Path("logs").mkdir(exist_ok=True)
    
    # Estabelecer conexão com o banco de dados
    conn = create_connection(db_params)
    
    # Verificar tabelas antes de aplicar RLS
    tables = [
        "empresa", "usuario", "usuario_empresa", "cliente", "fornecedor", 
        "categoria", "centro_custo", "conta_bancaria", "forma_pagamento", 
        "lancamento", "lancamento_anexo", "venda", "parcela", "log_atividade"
    ]
    
    missing_tables = [table for table in tables if not check_table_exists(conn, table)]
    if missing_tables:
        logger.warning(f"As seguintes tabelas não existem: {', '.join(missing_tables)}")
        proceed = input("Deseja continuar? (y/n): ").lower() == 'y'
        if not proceed:
            logger.info("Operação cancelada pelo usuário.")
            sys.exit(0)
    
    # Verificar RLS atual
    tables_with_rls = [table for table in tables if check_table_exists(conn, table) and check_rls_enabled(conn, table)]
    if tables_with_rls:
        logger.info(f"As seguintes tabelas já têm RLS habilitado: {', '.join(tables_with_rls)}")
    
    # Executar o arquivo SQL
    success = execute_sql_file(conn, sql_file_path)
    
    # Verificar RLS após execução
    if success:
        tables_with_rls_after = [table for table in tables if check_table_exists(conn, table) and check_rls_enabled(conn, table)]
        if tables_with_rls_after:
            logger.info(f"Tabelas com RLS habilitado após execução: {', '.join(tables_with_rls_after)}")
        
        tables_missing_rls = [table for table in tables if check_table_exists(conn, table) and not check_rls_enabled(conn, table)]
        if tables_missing_rls:
            logger.warning(f"As seguintes tabelas ainda não têm RLS habilitado: {', '.join(tables_missing_rls)}")
    
    # Fechar conexão
    conn.close()
    logger.info("Conexão com o banco de dados fechada.")
    
    if success:
        logger.info("Configuração de RLS aplicada com sucesso!")
        return 0
    else:
        logger.error("Falha ao aplicar configuração de RLS.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 