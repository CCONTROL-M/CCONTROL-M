#!/usr/bin/env python
"""
Script para realizar backup do banco de dados, incluindo todas as tabelas.
Específico para CCONTROL-M, com tratamento especial para tabelas com políticas RLS.
"""

import os
import sys
import logging
import argparse
import datetime
import subprocess
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Definir tabelas que possuem políticas RLS
RLS_TABLES = [
    'usuarios', 'clientes', 'produtos', 'vendas', 'categorias', 
    'lancamentos', 'parcelas', 'formas_pagamento', 'contas_bancarias',
    'fornecedores', 'centro_custos', 'logs_sistema', 'empresas', 
    'usuario_empresa', 'contas_pagar', 'contas_receber', 'permissoes',
    'permissoes_usuario'
]

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Realizar backup do banco de dados do CCONTROL-M.')
    parser.add_argument('--output-dir', type=str, default='./backups',
                      help='Diretório onde os backups serão salvos (padrão: ./backups)')
    parser.add_argument('--env-file', type=str, default='.env',
                      help='Arquivo .env com as variáveis de ambiente (padrão: .env)')
    parser.add_argument('--include-schema', action='store_true',
                      help='Incluir definições de schema no backup')
    parser.add_argument('--include-rls', action='store_true',
                      help='Incluir políticas RLS no backup')
    parser.add_argument('--only-rls-tables', action='store_true',
                      help='Backup apenas das tabelas com políticas RLS')
    
    return parser.parse_args()

def get_database_credentials():
    """Obter credenciais do banco de dados das variáveis de ambiente."""
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    if not all([db_host, db_port, db_name, db_user, db_password]):
        # Tentar obter de DATABASE_URL
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            # Parse da URL de conexão
            # Formato: postgresql://user:password@host:port/dbname
            try:
                # Remover prefixo
                if '://' in db_url:
                    db_url = db_url.split('://')[1]
                
                # Extrair credenciais
                user_pass, host_port_name = db_url.split('@')
                
                if ':' in user_pass:
                    db_user, db_password = user_pass.split(':')
                else:
                    db_user = user_pass
                    db_password = ""
                
                # Extrair host, port e name
                if '/' in host_port_name:
                    host_port, db_name = host_port_name.split('/')
                    
                    if ':' in host_port:
                        db_host, db_port = host_port.split(':')
                    else:
                        db_host = host_port
                        db_port = "5432"  # Porta padrão
                else:
                    db_host = host_port_name
                    db_port = "5432"
                    db_name = "postgres"
            except Exception as e:
                logger.error(f"Erro ao fazer parse da DATABASE_URL: {e}")
                raise ValueError("Credenciais de banco de dados insuficientes")
        else:
            raise ValueError("Credenciais de banco de dados insuficientes")
    
    return {
        'host': db_host,
        'port': db_port,
        'name': db_name,
        'user': db_user,
        'password': db_password
    }

def backup_database(creds, output_dir, include_schema=True, include_rls=True, only_rls_tables=False):
    """Realizar backup do banco de dados."""
    # Criar diretório de backup se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Gerar nome do arquivo de backup
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"ccontrol_backup_{timestamp}.sql"
    backup_path = os.path.join(output_dir, backup_filename)
    
    # Preparar comando pg_dump
    env = os.environ.copy()
    env['PGPASSWORD'] = creds['password']
    
    cmd = [
        'pg_dump',
        '--host', creds['host'],
        '--port', creds['port'],
        '--username', creds['user'],
        '--dbname', creds['name'],
        '--file', backup_path,
        '--format', 'plain'
    ]
    
    # Opções adicionais
    if not include_schema:
        cmd.append('--data-only')
    
    if only_rls_tables:
        for table in RLS_TABLES:
            cmd.extend(['--table', f'public.{table}'])
    
    if include_rls:
        cmd.append('--section=pre-data')
        cmd.append('--section=data')
        cmd.append('--section=post-data')
    
    # Executar backup
    logger.info(f"Iniciando backup do banco de dados para {backup_path}")
    try:
        subprocess.run(cmd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Backup concluído com sucesso: {backup_path}")
        
        # Adicionar políticas RLS ao backup se solicitado
        if include_rls:
            backup_rls_policies(creds, backup_path)
        
        return backup_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar pg_dump: {e}")
        logger.error(f"Saída de erro: {e.stderr.decode()}")
        raise

def backup_rls_policies(creds, backup_path):
    """Adicionar políticas RLS ao arquivo de backup."""
    logger.info("Exportando políticas RLS...")
    
    # SQL para extrair todas as políticas RLS
    rls_sql = """
    SELECT 'ALTER TABLE ' || tablename || ' ENABLE ROW LEVEL SECURITY;' as enable_rls,
           'CREATE POLICY "' || policyname || '" ON ' || tablename || 
           ' FOR ' || cmd || 
           CASE WHEN qual IS NOT NULL THEN ' USING (' || qual || ')' ELSE '' END ||
           CASE WHEN with_check IS NOT NULL THEN ' WITH CHECK (' || with_check || ')' ELSE '' END || ';' as policy_def
    FROM pg_policies
    WHERE schemaname = 'public'
    ORDER BY tablename, policyname;
    """
    
    env = os.environ.copy()
    env['PGPASSWORD'] = creds['password']
    
    cmd = [
        'psql',
        '--host', creds['host'],
        '--port', creds['port'],
        '--username', creds['user'],
        '--dbname', creds['name'],
        '--tuples-only',
        '--command', rls_sql
    ]
    
    try:
        result = subprocess.run(cmd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Adicionar políticas ao arquivo de backup
        with open(backup_path, 'a') as f:
            f.write("\n\n-- RLS POLICIES\n")
            f.write("-- Generated by CCONTROL-M backup script\n\n")
            
            # Processar resultado
            rls_policies = result.stdout.decode().strip().split('\n')
            for policy in rls_policies:
                if policy.strip():
                    f.write(f"{policy.strip()}\n")
            
        logger.info(f"Políticas RLS adicionadas ao backup: {len(rls_policies)} políticas")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao extrair políticas RLS: {e}")
        logger.error(f"Saída de erro: {e.stderr.decode()}")

def main():
    """Função principal."""
    args = parse_args()
    
    # Carregar arquivo .env específico se fornecido
    if args.env_file != '.env':
        load_dotenv(args.env_file)
    
    try:
        # Obter credenciais do banco de dados
        creds = get_database_credentials()
        
        # Realizar backup
        backup_path = backup_database(
            creds, 
            args.output_dir,
            include_schema=args.include_schema,
            include_rls=args.include_rls, 
            only_rls_tables=args.only_rls_tables
        )
        
        # Compactar backup
        try:
            import gzip
            with open(backup_path, 'rb') as f_in:
                with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remover arquivo original após compactação
            os.remove(backup_path)
            logger.info(f"Backup compactado: {backup_path}.gz")
            
        except ImportError:
            logger.warning("Módulo gzip não disponível. Backup não compactado.")
        
    except Exception as e:
        logger.error(f"Erro durante o backup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 