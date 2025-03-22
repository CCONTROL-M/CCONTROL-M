#!/bin/bash
# Script de restauração do CCONTROL-M a partir de um backup

# Configurações
BACKUP_DIR="/opt/ccontrol-m/backups"
INSTALL_DIR="/opt/ccontrol-m"
LOG_FILE="${INSTALL_DIR}/logs/restore.log"
DOCKER_COMPOSE_FILE="${INSTALL_DIR}/docker-compose.prod.yml"
DB_CONTAINER="ccontrol-m-postgres"
DB_NAME="ccontrolm_prod"
DB_USER="postgres"
UPLOAD_DIR="${INSTALL_DIR}/backend/uploads"

# Definir cores para melhor visualização
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Verificar se o backup_file foi fornecido como argumento
if [ $# -eq 0 ]; then
    log_error "Nenhum arquivo de backup fornecido"
    log_message "Uso: $0 <arquivo_de_backup>"
    log_message "Backups disponíveis:"
    
    # Listar arquivos de backup disponíveis
    if [ -d "${BACKUP_DIR}" ]; then
        ls -lh "${BACKUP_DIR}" | grep ".tar.gz" | awk '{print "  " $9 " (" $5 ")"}'
    else
        log_error "Diretório de backups não encontrado: ${BACKUP_DIR}"
    fi
    
    exit 1
fi

BACKUP_FILE=$1

# Verificar se o arquivo de backup existe
if [ ! -f "${BACKUP_FILE}" ] && [ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    log_error "Arquivo de backup não encontrado: ${BACKUP_FILE}"
    exit 1
fi

# Definir caminho completo para o arquivo de backup
if [ -f "${BACKUP_FILE}" ]; then
    BACKUP_FULL_PATH="${BACKUP_FILE}"
else
    BACKUP_FULL_PATH="${BACKUP_DIR}/${BACKUP_FILE}"
fi

# Verificar se o sistema está em execução
if [ -f "${DOCKER_COMPOSE_FILE}" ]; then
    log_message "Verificando se os containers estão em execução..."
    if docker-compose -f "${DOCKER_COMPOSE_FILE}" ps | grep -q "Up"; then
        log_warning "O sistema está em execução. É recomendado parar os serviços antes da restauração."
        read -p "Deseja continuar mesmo assim? (s/N): " CONTINUE
        if [[ ! "$CONTINUE" =~ ^[Ss]$ ]]; then
            log_message "Restauração cancelada pelo usuário."
            exit 0
        fi
        
        log_message "Parando os serviços do CCONTROL-M..."
        docker-compose -f "${DOCKER_COMPOSE_FILE}" down
        log_success "Serviços parados com sucesso"
    else
        log_message "Os serviços do CCONTROL-M não estão em execução. Continuando restauração..."
    fi
else
    log_warning "Arquivo docker-compose.prod.yml não encontrado em ${INSTALL_DIR}"
    read -p "Deseja continuar mesmo assim? (s/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Ss]$ ]]; then
        log_message "Restauração cancelada pelo usuário."
        exit 0
    fi
fi

# Criar diretório temporário para extração
TEMP_DIR=$(mktemp -d)
log_message "Extraindo backup para diretório temporário: ${TEMP_DIR}"

# Extrair o arquivo de backup
if tar -xzf "${BACKUP_FULL_PATH}" -C "${TEMP_DIR}"; then
    log_success "Backup extraído com sucesso"
else
    log_error "Falha ao extrair o arquivo de backup"
    rm -rf "${TEMP_DIR}"
    exit 1
fi

# Encontrar arquivos extraídos
DB_DUMP=$(find "${TEMP_DIR}" -name "*.dump" | head -n 1)
UPLOADS_ARCHIVE=$(find "${TEMP_DIR}" -name "uploads_*.tar.gz" | head -n 1)

# Verificar se os arquivos necessários foram encontrados
if [ -z "${DB_DUMP}" ]; then
    log_error "Arquivo de dump do banco de dados não encontrado no backup"
    rm -rf "${TEMP_DIR}"
    exit 1
fi

# Restaurar o banco de dados
log_message "Iniciando restauração do banco de dados..."

# Verificar se o container do PostgreSQL está em execução
if docker ps | grep -q "${DB_CONTAINER}"; then
    log_message "Container do PostgreSQL está em execução"
else
    log_message "Iniciando container do PostgreSQL..."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d postgres
    
    # Aguardar o container iniciar
    log_message "Aguardando o PostgreSQL iniciar..."
    sleep 10
    
    # Verificar novamente
    if ! docker ps | grep -q "${DB_CONTAINER}"; then
        log_error "Falha ao iniciar container do PostgreSQL"
        rm -rf "${TEMP_DIR}"
        exit 1
    fi
fi

# Restaurar o banco de dados
log_message "Copiando dump para o container..."
docker cp "${DB_DUMP}" "${DB_CONTAINER}:/tmp/db.dump"

log_message "Verificando se o banco de dados existe..."
if docker exec "${DB_CONTAINER}" psql -U "${DB_USER}" -lqt | grep -q "${DB_NAME}"; then
    log_warning "Banco de dados ${DB_NAME} já existe. Recriando..."
    
    # Desconectar todas as conexões ativas e remover o banco de dados
    docker exec "${DB_CONTAINER}" psql -U "${DB_USER}" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}';"
    docker exec "${DB_CONTAINER}" psql -U "${DB_USER}" -c "DROP DATABASE IF EXISTS ${DB_NAME};"
    docker exec "${DB_CONTAINER}" psql -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME};"
    
    log_success "Banco de dados recriado com sucesso"
else
    log_message "Criando banco de dados ${DB_NAME}..."
    docker exec "${DB_CONTAINER}" psql -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME};"
    log_success "Banco de dados criado com sucesso"
fi

# Restaurar o dump
log_message "Restaurando o banco de dados a partir do dump..."
if docker exec "${DB_CONTAINER}" pg_restore -U "${DB_USER}" -d "${DB_NAME}" -c "/tmp/db.dump"; then
    log_success "Banco de dados restaurado com sucesso"
    
    # Limpar arquivo temporário
    docker exec "${DB_CONTAINER}" rm "/tmp/db.dump"
else
    log_error "Falha ao restaurar o banco de dados"
    docker exec "${DB_CONTAINER}" rm "/tmp/db.dump"
    rm -rf "${TEMP_DIR}"
    exit 1
fi

# Restaurar uploads se o arquivo existir
if [ -n "${UPLOADS_ARCHIVE}" ]; then
    log_message "Iniciando restauração dos arquivos de upload..."
    
    # Criar diretório de backup para arquivos atuais
    UPLOADS_BACKUP="${UPLOAD_DIR}_backup_$(date +%Y%m%d%H%M%S)"
    
    # Verificar se o diretório de uploads existe e fazer backup
    if [ -d "${UPLOAD_DIR}" ]; then
        log_message "Fazendo backup dos arquivos de upload atuais para ${UPLOADS_BACKUP}..."
        mv "${UPLOAD_DIR}" "${UPLOADS_BACKUP}"
        log_success "Backup dos arquivos atuais concluído"
    fi
    
    # Criar diretório de uploads se não existir
    mkdir -p "${UPLOAD_DIR}"
    
    # Extrair arquivos
    log_message "Extraindo arquivos de upload..."
    if tar -xzf "${UPLOADS_ARCHIVE}" -C "${INSTALL_DIR}/backend/"; then
        log_success "Arquivos de upload restaurados com sucesso"
    else
        log_error "Falha ao extrair arquivos de upload"
        
        # Restaurar backup anterior
        if [ -d "${UPLOADS_BACKUP}" ]; then
            log_message "Restaurando arquivos de upload anteriores..."
            rm -rf "${UPLOAD_DIR}"
            mv "${UPLOADS_BACKUP}" "${UPLOAD_DIR}"
        fi
    fi
else
    log_warning "Arquivo de uploads não encontrado no backup. Apenas o banco de dados foi restaurado."
fi

# Limpar arquivos temporários
log_message "Limpando arquivos temporários..."
rm -rf "${TEMP_DIR}"

# Reiniciar os serviços
log_message "Reiniciando os serviços..."
if [ -f "${DOCKER_COMPOSE_FILE}" ]; then
    docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d
    log_success "Serviços reiniciados com sucesso"
else
    log_warning "Arquivo docker-compose.prod.yml não encontrado. Não foi possível reiniciar os serviços automaticamente."
    log_message "Execute 'docker-compose -f ${DOCKER_COMPOSE_FILE} up -d' manualmente para iniciar os serviços."
fi

log_success "Restauração concluída com sucesso!"
log_message "Data da restauração: $(date)"
log_message "Arquivo de backup utilizado: ${BACKUP_FULL_PATH}"
log_message "============================================"

exit 0 