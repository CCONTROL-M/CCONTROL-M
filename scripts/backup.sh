#!/bin/bash
# Script de backup automático do CCONTROL-M
# Realiza backup do banco de dados e arquivos de upload

# Configurações
BACKUP_DIR="/opt/ccontrol-m/backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
RETENTION_DAYS=30
DB_CONTAINER="ccontrol-m-postgres"
DB_NAME="ccontrolm_prod"
DB_USER="postgres"
UPLOADS_DIR="/opt/ccontrol-m/backend/uploads"
S3_BUCKET="ccontrol-m-backups"
BACKUP_FILENAME="ccontrol-m_backup_${DATE}"
LOG_FILE="/opt/ccontrol-m/logs/backup.log"

# Criar diretório de backup se não existir
mkdir -p "${BACKUP_DIR}"
mkdir -p "/opt/ccontrol-m/logs"

# Função para logar mensagens
log_message() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "${LOG_FILE}"
}

# Iniciar processo de backup
log_message "Iniciando backup do CCONTROL-M..."

# Backup do banco de dados
log_message "Realizando backup do banco de dados ${DB_NAME}..."
if docker exec "${DB_CONTAINER}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" -F c -f "/tmp/${DB_NAME}.dump"; then
    docker cp "${DB_CONTAINER}:/tmp/${DB_NAME}.dump" "${BACKUP_DIR}/${DB_NAME}_${DATE}.dump"
    docker exec "${DB_CONTAINER}" rm "/tmp/${DB_NAME}.dump"
    log_message "Backup do banco de dados concluído com sucesso."
else
    log_message "ERRO: Falha ao realizar backup do banco de dados."
    exit 1
fi

# Backup dos arquivos de upload
log_message "Realizando backup dos arquivos de upload..."
if tar -czf "${BACKUP_DIR}/uploads_${DATE}.tar.gz" -C "$(dirname "${UPLOADS_DIR}")" "$(basename "${UPLOADS_DIR}")"; then
    log_message "Backup dos arquivos de upload concluído com sucesso."
else
    log_message "ERRO: Falha ao realizar backup dos arquivos de upload."
    exit 1
fi

# Criar backup completo
log_message "Criando arquivo de backup completo..."
if tar -czf "${BACKUP_DIR}/${BACKUP_FILENAME}.tar.gz" -C "${BACKUP_DIR}" "${DB_NAME}_${DATE}.dump" "uploads_${DATE}.tar.gz"; then
    log_message "Arquivo de backup completo criado com sucesso."
    
    # Remover arquivos temporários
    rm "${BACKUP_DIR}/${DB_NAME}_${DATE}.dump" "${BACKUP_DIR}/uploads_${DATE}.tar.gz"
else
    log_message "ERRO: Falha ao criar arquivo de backup completo."
    exit 1
fi

# Sincronizar com S3 (se configurado)
if command -v aws > /dev/null; then
    log_message "Enviando backup para o Amazon S3..."
    if aws s3 cp "${BACKUP_DIR}/${BACKUP_FILENAME}.tar.gz" "s3://${S3_BUCKET}/${BACKUP_FILENAME}.tar.gz"; then
        log_message "Backup enviado para o S3 com sucesso."
    else
        log_message "AVISO: Falha ao enviar backup para o S3."
    fi
else
    log_message "AVISO: AWS CLI não encontrado. Backup não foi enviado para o S3."
fi

# Remover backups antigos
log_message "Removendo backups com mais de ${RETENTION_DAYS} dias..."
find "${BACKUP_DIR}" -name "ccontrol-m_backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete
log_message "Limpeza de backups antigos concluída."

# Verificar espaço em disco
DISK_USAGE=$(df -h "${BACKUP_DIR}" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "${DISK_USAGE}" -gt 80 ]; then
    log_message "AVISO: Espaço em disco está acima de 80% (${DISK_USAGE}%). Considere liberar espaço."
fi

# Finalizar processo de backup
log_message "Backup concluído com sucesso. Arquivo: ${BACKUP_DIR}/${BACKUP_FILENAME}.tar.gz"
log_message "Tamanho do backup: $(du -h "${BACKUP_DIR}/${BACKUP_FILENAME}.tar.gz" | cut -f1)"
log_message "============================================"

exit 0 