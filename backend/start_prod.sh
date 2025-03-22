#!/bin/bash
set -e

# Configurações
LOG_DIR="/app/logs"
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"
APP_LOG="$LOG_DIR/app.log"
MAX_LOG_SIZE=100M  # Tamanho máximo de cada arquivo de log
MAX_LOG_FILES=10   # Quantidade máxima de arquivos de log a manter
WORKERS=${WORKERS:-4}  # Quantidade de workers (usa valor da variável de ambiente ou padrão 4)
PORT=${PORT:-8000}     # Porta (usa valor da variável de ambiente ou padrão 8000)

# Criar diretório de logs se não existir
mkdir -p "$LOG_DIR"

# Verificar existência do arquivo .env.prod
if [ -f .env.prod ]; then
    echo "Carregando variáveis de ambiente de .env.prod"
    export $(grep -v '^#' .env.prod | xargs)
else
    echo "Arquivo .env.prod não encontrado, usando variáveis padrão"
fi

# Verificar se logrotate está disponível
if command -v logrotate &> /dev/null; then
    echo "Configurando rotação de logs com logrotate"
    cat > /tmp/ccontrol-logrotate.conf << EOF
$ACCESS_LOG $ERROR_LOG $APP_LOG {
    size $MAX_LOG_SIZE
    rotate $MAX_LOG_FILES
    compress
    delaycompress
    missingok
    notifempty
    maxage 30
    dateext
    dateformat -%Y%m%d
    sharedscripts
    postrotate
        kill -USR1 \$(cat /tmp/gunicorn.pid 2>/dev/null) 2>/dev/null || true
    endscript
}
EOF
    
    # Agendar logrotate para execução diária
    (crontab -l 2>/dev/null || echo "") | grep -v "ccontrol-logrotate" | { cat; echo "0 0 * * * /usr/sbin/logrotate /tmp/ccontrol-logrotate.conf --state /tmp/logrotate-state"; } | crontab -
    
    # Adicionar limpeza semanal para arquivos mais antigos que 30 dias
    (crontab -l 2>/dev/null || echo "") | grep -v "ccontrol-logs-cleanup" | { cat; echo "0 1 * * 0 find $LOG_DIR -name \"*.gz\" -type f -mtime +30 -delete"; } | crontab -
else
    echo "logrotate não encontrado, usando rotação manual de logs"
    
    # Função para rotação manual de logs
    rotate_log() {
        local log_file=$1
        local max_size=$2
        local max_files=$3
        
        # Verificar se o arquivo de log existe
        if [ ! -f "$log_file" ]; then
            return
        fi
        
        # Verificar tamanho do arquivo de log
        local size=$(du -b "$log_file" | cut -f1)
        local max_size_bytes=$(echo "$max_size" | sed 's/M/*1024*1024/' | bc)
        
        if [ "$size" -gt "$max_size_bytes" ]; then
            echo "Rotacionando $log_file (tamanho: $size bytes)"
            
            # Mover arquivos antigos
            for i in $(seq $max_files -1 1); do
                if [ -f "${log_file}.$i" ]; then
                    if [ "$i" -eq "$max_files" ]; then
                        # Remover arquivo mais antigo
                        rm -f "${log_file}.$i"
                    else
                        # Mover arquivo para próximo índice
                        mv "${log_file}.$i" "${log_file}.$((i+1))"
                    fi
                fi
            done
            
            # Mover arquivo atual
            mv "$log_file" "${log_file}.1"
            
            # Criar novo arquivo vazio
            touch "$log_file"
            
            # Comprimir arquivos antigos
            gzip -f "${log_file}.1"
            
            # Reiniciar serviço para reconhecer nova rotação
            if [ -f /tmp/gunicorn.pid ]; then
                kill -USR1 $(cat /tmp/gunicorn.pid) 2>/dev/null || true
            fi
        fi
    }
    
    # Agendar rotação manual e limpeza via cron
    (crontab -l 2>/dev/null || echo "") | grep -v "ccontrol-manual-rotate" | { cat; echo "0 0 * * * for f in $ACCESS_LOG $ERROR_LOG $APP_LOG; do $0 rotate_log \$f $MAX_LOG_SIZE $MAX_LOG_FILES; done"; } | crontab -
    
    # Adicionar limpeza de arquivos antigos
    (crontab -l 2>/dev/null || echo "") | grep -v "ccontrol-logs-cleanup" | { cat; echo "0 1 * * 0 find $LOG_DIR -name \"*.gz\" -type f -mtime +30 -delete"; } | crontab -
fi

# Função para lidar com sinais de término
cleanup() {
    echo "Recebido sinal para encerrar, parando aplicação..."
    
    # Matar o processo gunicorn
    if [ -f /tmp/gunicorn.pid ]; then
        kill -TERM $(cat /tmp/gunicorn.pid) 2>/dev/null || true
    fi
    
    # Aguardar até 30 segundos pelo término gracioso
    count=0
    while [ -f /tmp/gunicorn.pid ] && [ $count -lt 30 ]; do
        sleep 1
        count=$((count+1))
    done
    
    # Forçar término se demorar muito
    if [ -f /tmp/gunicorn.pid ]; then
        echo "Forçando encerramento..."
        kill -9 $(cat /tmp/gunicorn.pid) 2>/dev/null || true
    fi
    
    echo "Aplicação encerrada"
    exit 0
}

# Registrar handlers para sinais
trap cleanup SIGINT SIGTERM

echo "Iniciando servidor CCONTROL-M em ambiente de produção na porta $PORT com $WORKERS workers"

# Iniciar o servidor gunicorn com uvicorn worker
gunicorn "app.main:app" \
    --bind "0.0.0.0:$PORT" \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --pid /tmp/gunicorn.pid \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG" \
    --log-level info \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --forwarded-allow-ips '*' \
    --capture-output \
    --preload \
    --daemon

echo "Servidor iniciado em segundo plano, monitorando logs..."

# Iniciar monitoramento do servidor
if [ "$ENABLE_HEALTH_CHECK" = "True" ] || [ "$ENABLE_HEALTH_CHECK" = "true" ]; then
    echo "Health check ativado, monitorando estado do servidor"
    
    # Loop para monitoramento
    while true; do
        # Verificar se o processo ainda está rodando
        if ! kill -0 $(cat /tmp/gunicorn.pid 2>/dev/null) 2>/dev/null; then
            echo "Servidor não está mais rodando, reiniciando..."
            
            # Reiniciar o servidor
            gunicorn "app.main:app" \
                --bind "0.0.0.0:$PORT" \
                --workers $WORKERS \
                --worker-class uvicorn.workers.UvicornWorker \
                --pid /tmp/gunicorn.pid \
                --access-logfile "$ACCESS_LOG" \
                --error-logfile "$ERROR_LOG" \
                --log-level info \
                --timeout 120 \
                --graceful-timeout 30 \
                --keep-alive 5 \
                --forwarded-allow-ips '*' \
                --capture-output \
                --preload \
                --daemon
                
            echo "Servidor reiniciado"
        fi
        
        # Verificar health check via HTTP
        sleep 30
        if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/health | grep -q "2[0-9][0-9]"; then
            echo "Health check falhou, reiniciando servidor..."
            
            # Matar o processo atual se estiver rodando
            if [ -f /tmp/gunicorn.pid ]; then
                kill -TERM $(cat /tmp/gunicorn.pid) 2>/dev/null || true
                sleep 5
            fi
            
            # Reiniciar o servidor
            gunicorn "app.main:app" \
                --bind "0.0.0.0:$PORT" \
                --workers $WORKERS \
                --worker-class uvicorn.workers.UvicornWorker \
                --pid /tmp/gunicorn.pid \
                --access-logfile "$ACCESS_LOG" \
                --error-logfile "$ERROR_LOG" \
                --log-level info \
                --timeout 120 \
                --graceful-timeout 30 \
                --keep-alive 5 \
                --forwarded-allow-ips '*' \
                --capture-output \
                --preload \
                --daemon
                
            echo "Servidor reiniciado após falha no health check"
        fi
        
        # Exibir últimas linhas do log para monitoramento
        tail -n 50 "$APP_LOG" "$ERROR_LOG" 2>/dev/null || true
        sleep 30
    done
else
    # Se health check estiver desativado, apenas seguir o log
    tail -f "$APP_LOG" "$ERROR_LOG" 2>/dev/null || true
fi 