#!/usr/bin/env python
"""
Script para verificar as configurações de Row-Level Security (RLS) em todas as tabelas do CCONTROL-M no PostgreSQL/Supabase.
"""

import os
import sys
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from tabulate import tabulate

# Adicionar diretório pai ao path para importar configurações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config.settings import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Lista de tabelas que deveriam ter RLS habilitado (todas as tabelas principais do sistema)
EXPECTED_TABLES = [
    "empresas",
    "usuarios",
    "clientes",
    "fornecedores",
    "contas_bancarias",
    "formas_pagamento",
    "categorias",
    "centro_custos",
    "vendas",
    "lancamentos",
    "logs_sistema"
]

def check_rls_status():
    """
    Verifica o status do RLS em todas as tabelas do CCONTROL-M.
    """
    conn = None
    try:
        # Conectar ao banco de dados usando a string de conexão
        logger.info("Conectando ao banco de dados...")
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Criar cursor
        cursor = conn.cursor()
        
        # Identificar tabelas existentes
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # Filtrar lista de tabelas esperadas para apenas as que existem
        existing_expected_tables = [table for table in EXPECTED_TABLES if table in existing_tables]
        
        # Consultar o status RLS das tabelas
        cursor.execute("""
        SELECT c.relname as table_name, c.relrowsecurity 
        FROM pg_catalog.pg_class c 
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace 
        WHERE n.nspname = 'public' AND c.relkind = 'r';
        """)
        
        rows = cursor.fetchall()
        all_tables = {row[0]: row[1] for row in rows}
        
        # Verificar RLS apenas nas tabelas que existem
        results = []
        rls_disabled_tables = []
        
        # Primeiro mostrar as tabelas existentes
        for table in existing_expected_tables:
            if table in all_tables:
                results.append([table, "✅" if all_tables[table] else "❌", "Sim"])
                if not all_tables[table]:
                    rls_disabled_tables.append(table)
            else:
                # Este caso não deveria ocorrer, mas é um fallback
                results.append([table, "Não disponível", "Sim"])
        
        # Depois mostrar as tabelas que não existem
        non_existing_tables = [table for table in EXPECTED_TABLES if table not in existing_tables]
        for table in non_existing_tables:
            results.append([table, "N/A", "Não"])
        
        # Imprimir resultados em formato de tabela
        print("\n=== STATUS DO ROW-LEVEL SECURITY (RLS) ===\n")
        print(tabulate(results, headers=["Tabela", "RLS Ativo", "Existe"], tablefmt="grid"))
        
        # Resumo
        total_existing_tables = len(existing_expected_tables)
        rls_enabled = total_existing_tables - len(rls_disabled_tables)
        
        print(f"\nResumo:")
        print(f"- Total de tabelas esperadas: {len(EXPECTED_TABLES)}")
        print(f"- Tabelas existentes: {total_existing_tables}")
        print(f"- Tabelas com RLS ativado: {rls_enabled}")
        print(f"- Tabelas com RLS desativado: {len(rls_disabled_tables)}")
        
        if rls_disabled_tables:
            print("\nTabelas com RLS desativado:")
            for table in rls_disabled_tables:
                print(f"- {table}")
            
            print("\nPara ativar o RLS nas tabelas existentes, execute:")
            print("python scripts/apply_rls.py")
        elif total_existing_tables > 0 and rls_enabled == total_existing_tables:
            print("\n✅ Todas as tabelas existentes têm RLS ativado!")
        
        # Verificar políticas
        if rls_enabled > 0:
            logger.info("Verificando políticas RLS...")
            query_policies = """
            SELECT tablename, policyname, permissive, cmd, qual
            FROM pg_policies
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname;
            """
            
            cursor.execute(query_policies)
            policies = cursor.fetchall()
            
            if policies:
                policy_results = []
                for p in policies:
                    policy_results.append([p[0], p[1], p[2], p[3], p[4]])
                
                print("\n=== POLÍTICAS RLS CONFIGURADAS ===\n")
                print(tabulate(policy_results, 
                              headers=["Tabela", "Política", "Permissiva", "Comando", "Condição"], 
                              tablefmt="grid"))
            else:
                print("\nNenhuma política RLS encontrada!")
                print("Execute o script para aplicar as políticas:")
                print("python scripts/apply_rls.py")
        
        # Fechar cursor
        cursor.close()
    
    except Exception as e:
        logger.error(f"Erro ao verificar RLS: {str(e)}")
    
    finally:
        # Fechar conexão
        if conn:
            conn.close()
            logger.info("Conexão fechada")


if __name__ == "__main__":
    check_rls_status() 