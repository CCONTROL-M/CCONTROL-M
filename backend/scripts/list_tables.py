#!/usr/bin/env python
"""
Script para listar todas as tabelas existentes no banco de dados.
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

def list_tables():
    """
    Lista todas as tabelas existentes no banco de dados.
    """
    conn = None
    try:
        # Conectar ao banco de dados
        logger.info("Conectando ao banco de dados...")
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Criar cursor
        cursor = conn.cursor()
        
        # Consultar tabelas
        cursor.execute("""
        SELECT 
            table_name 
        FROM 
            information_schema.tables 
        WHERE 
            table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        ORDER BY
            table_name
        """)
        
        rows = cursor.fetchall()
        
        # Imprimir resultados
        if rows:
            print("\n=== TABELAS EXISTENTES ===\n")
            table_list = [[i+1, row[0]] for i, row in enumerate(rows)]
            print(tabulate(table_list, headers=["#", "Nome da Tabela"], tablefmt="grid"))
            print(f"\nTotal de tabelas: {len(rows)}")
        else:
            print("\nNenhuma tabela encontrada no banco de dados.")
        
        # Fechar cursor
        cursor.close()
    
    except Exception as e:
        logger.error(f"Erro ao listar tabelas: {str(e)}")
    
    finally:
        # Fechar conexão
        if conn:
            conn.close()
            logger.info("Conexão fechada")


if __name__ == "__main__":
    list_tables() 