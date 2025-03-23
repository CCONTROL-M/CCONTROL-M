#!/bin/bash
# Script de restauração do banco de dados PostgreSQL para o CCONTROL-M

# Definir caminho do arquivo .env.prod
ENV_FILE="../backend/.env.prod"

# Definir cores para melhor visualização
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório de backups
BACKUP_DIR="../backups"
LOG_FILE="../logs/restore.log"

# Criar diretório de logs se não existir
mkdir -p "../logs"

# Funções para exibir mensagens
log_message() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}" | tee -a "${LOG_FILE}"
}

# Verificar se o arquivo .env.prod existe
if [ ! -f "$ENV_FILE" ]; then
    log_error "Arquivo $ENV_FILE não encontrado."
    exit 1
fi

# Carregar variáveis do arquivo .env.prod
log_message "Carregando configurações do arquivo $ENV_FILE..."
export $(grep -v '^#' $ENV_FILE | xargs)

# Extrair informações do banco de dados da variável DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    log_error "Variável DATABASE_URL não encontrada no arquivo .env.prod."
    exit 1
fi

# Extrair informações do DATABASE_URL no formato: postgresql://user:password@host:port/dbname
DB_USER=$(echo $DATABASE_URL | awk -F '//' '{print $2}' | awk -F ':' '{print $1}')
DB_PASSWORD=$(echo $DATABASE_URL | awk -F ':' '{print $3}' | awk -F '@' '{print $1}')
DB_HOST=$(echo $DATABASE_URL | awk -F '@' '{print $2}' | awk -F ':' '{print $1}')
DB_PORT=$(echo $DATABASE_URL | awk -F ':' '{print $4}' | awk -F '/' '{print $1}')
DB_NAME=$(echo $DATABASE_URL | awk -F '/' '{print $NF}')

# Verificar se o backup_file foi fornecido como argumento
if [ $# -eq 0 ]; then
    log_error "Nenhum arquivo de backup fornecido"
    log_message "Uso: $0 <arquivo_de_backup>"
    log_message "Backups disponíveis:"
    
    # Listar arquivos de backup disponíveis
    if [ -d "${BACKUP_DIR}" ]; then
        ls -lht "${BACKUP_DIR}" | grep ".sql" | awk '{print "  " $9 " (" $5 ")"}'
    else
        log_error "Diretório de backups não encontrado: ${BACKUP_DIR}"
    fi
    
    exit 1
fi

BACKUP_FILE=$1

# Verificar se o arquivo de backup existe
if [ ! -f "${BACKUP_FILE}" ] && [ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    log_error "Arquivo de backup não encontrado: ${BACKUP_FILE}"
    log_message "Verifique se o arquivo existe no diretório ${BACKUP_DIR}"
    exit 1
fi

# Definir caminho completo para o arquivo de backup
if [ -f "${BACKUP_FILE}" ]; then
    BACKUP_FULL_PATH="${BACKUP_FILE}"
else
    BACKUP_FULL_PATH="${BACKUP_DIR}/${BACKUP_FILE}"
fi

log_message "Arquivo de backup encontrado: ${BACKUP_FULL_PATH}"
log_message "Tamanho do backup: $(du -h ${BACKUP_FULL_PATH} | cut -f1)"

# Solicitar confirmação para restauração
log_warning "Esta operação irá sobrescrever o banco de dados existente!"
log_warning "Todos os dados atuais serão perdidos e substituídos pelos dados do backup."
read -p "Tem certeza que deseja continuar? (s/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Ss]$ ]]; then
    log_message "Restauração cancelada pelo usuário."
    exit 0
fi

# Verificar se o pg_restore está disponível
if ! command -v pg_restore &> /dev/null; then
    log_error "Comando pg_restore não encontrado! Verifique se o PostgreSQL Client está instalado."
    exit 1
fi

# Iniciar processo de restauração
log_message "Iniciando restauração do banco de dados..."
log_message "Database: $DB_NAME, Host: $DB_HOST, Port: $DB_PORT, User: $DB_USER"

# Restaurar o banco de dados
log_message "Restaurando o banco de dados a partir do backup..."
PGPASSWORD=$DB_PASSWORD pg_restore -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c -v "${BACKUP_FULL_PATH}"

# Verificar se a restauração foi bem-sucedida
if [ $? -eq 0 ]; then
    log_success "Banco de dados restaurado com sucesso!"
else
    log_error "Ocorreu um erro durante a restauração do banco de dados."
    log_warning "Verifique os logs para mais detalhes."
    exit 1
fi

# Finalizar processo de restauração
log_success "Processo de restauração concluído com sucesso!"
log_message "Data da restauração: $(date)"
log_message "Arquivo de backup utilizado: ${BACKUP_FULL_PATH}"
log_message "============================================"

exit 0 