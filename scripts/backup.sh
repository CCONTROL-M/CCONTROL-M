#!/bin/bash
# Script de backup automático do PostgreSQL para o CCONTROL-M
# Realiza backup do banco de dados utilizando variáveis do .env.prod

# Definir caminho do arquivo .env.prod
ENV_FILE="../backend/.env.prod"

# Verificar se o arquivo .env.prod existe
if [ ! -f "$ENV_FILE" ]; then
    echo "Arquivo $ENV_FILE não encontrado."
    exit 1
fi

# Carregar variáveis do arquivo .env.prod
echo "Carregando configurações do arquivo $ENV_FILE..."
export $(grep -v '^#' $ENV_FILE | xargs)

# Extrair informações do banco de dados da variável DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "Variável DATABASE_URL não encontrada no arquivo .env.prod."
    exit 1
fi

# Extrair informações do DATABASE_URL no formato: postgresql://user:password@host:port/dbname
DB_USER=$(echo $DATABASE_URL | awk -F '//' '{print $2}' | awk -F ':' '{print $1}')
DB_PASSWORD=$(echo $DATABASE_URL | awk -F ':' '{print $3}' | awk -F '@' '{print $1}')
DB_HOST=$(echo $DATABASE_URL | awk -F '@' '{print $2}' | awk -F ':' '{print $1}')
DB_PORT=$(echo $DATABASE_URL | awk -F ':' '{print $4}' | awk -F '/' '{print $1}')
DB_NAME=$(echo $DATABASE_URL | awk -F '/' '{print $NF}')

# Configurações
BACKUP_DIR="../backups"
DATE=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=7
BACKUP_FILENAME="ccontrol-m_backup_${DATE}.sql"
LOG_FILE="../logs/backup.log"

# Criar diretório de backup se não existir
mkdir -p "${BACKUP_DIR}"
mkdir -p "../logs"

# Função para logar mensagens
log_message() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "${LOG_FILE}"
}

# Iniciar processo de backup
log_message "Iniciando backup do banco de dados PostgreSQL..."
log_message "Database: $DB_NAME, Host: $DB_HOST, Port: $DB_PORT, User: $DB_USER"

# Realizar o backup com pg_dump
log_message "Executando pg_dump..."
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -F c -f "${BACKUP_DIR}/${BACKUP_FILENAME}"

# Verificar se o backup foi bem-sucedido
if [ $? -eq 0 ]; then
    log_message "Backup concluído com sucesso: ${BACKUP_DIR}/${BACKUP_FILENAME}"
    log_message "Tamanho do backup: $(du -h "${BACKUP_DIR}/${BACKUP_FILENAME}" | cut -f1)"
else
    log_message "ERRO: Falha ao realizar o backup do banco de dados."
    exit 1
fi

# Remover backups antigos (manter apenas os últimos 7)
log_message "Removendo backups antigos (mantendo apenas os últimos ${RETENTION_DAYS})..."
ls -t "${BACKUP_DIR}"/ccontrol-m_backup_*.sql | tail -n +$((RETENTION_DAYS + 1)) | xargs -r rm

# Contar quantos backups sobraram
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/ccontrol-m_backup_*.sql 2>/dev/null | wc -l)
log_message "Total de backups armazenados: ${BACKUP_COUNT}"

# Verificar espaço em disco
DISK_USAGE=$(df -h "${BACKUP_DIR}" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "${DISK_USAGE}" -gt 80 ]; then
    log_message "AVISO: Espaço em disco está acima de 80% (${DISK_USAGE}%). Considere liberar espaço."
fi

# Finalizar processo de backup
log_message "Processo de backup finalizado com sucesso."
log_message "============================================"

exit 0 