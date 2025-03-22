#!/bin/bash
# Script de configuração do ambiente de produção para CCONTROL-M
# Este script instala todas as dependências necessárias e configura o ambiente inicial

# Definir cores para melhor visualização
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para exibir mensagens de progresso
print_message() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Função para exibir mensagens de sucesso
print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

# Função para exibir mensagens de erro
print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Função para exibir mensagens de aviso
print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}"
}

# Verificar se o script está sendo executado como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script precisa ser executado como root"
    print_message "Por favor, execute: sudo $0"
    exit 1
fi

# Configurações
INSTALL_DIR="/opt/ccontrol-m"
BACKEND_DIR="$INSTALL_DIR/backend"
LOG_DIR="$INSTALL_DIR/logs"
BACKUP_DIR="$INSTALL_DIR/backups"
NGINX_DIR="$INSTALL_DIR/nginx"
DOMAIN="ccontrol-m.seudominio.com.br"
DB_USER="postgres"
DB_PASS="postgres"
DB_NAME="ccontrolm_prod"
REDIS_PASS="redis"

# Criar diretório principal se não existir
print_message "Criando estrutura de diretórios..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$NGINX_DIR/conf"
mkdir -p "$NGINX_DIR/ssl"
mkdir -p "$NGINX_DIR/logs"
mkdir -p "$INSTALL_DIR/init-scripts"
chmod -R 755 "$INSTALL_DIR"
print_success "Estrutura de diretórios criada com sucesso"

# Atualizar o sistema
print_message "Atualizando o sistema..."
apt-get update && apt-get upgrade -y
print_success "Sistema atualizado com sucesso"

# Instalar dependências
print_message "Instalando dependências necessárias..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common \
    git \
    vim \
    htop \
    ufw \
    fail2ban \
    logrotate \
    certbot \
    python3-certbot-nginx \
    nginx-full \
    python3-pip \
    python3-dev \
    build-essential \
    libpq-dev \
    postgresql-client \
    jq
print_success "Dependências instaladas com sucesso"

# Instalar Docker se não estiver instalado
if ! command -v docker &> /dev/null; then
    print_message "Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $SUDO_USER
    systemctl enable docker
    systemctl start docker
    print_success "Docker instalado com sucesso"
else
    print_message "Docker já está instalado"
fi

# Instalar Docker Compose se não estiver instalado
if ! command -v docker-compose &> /dev/null; then
    print_message "Instalando Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    print_success "Docker Compose instalado com sucesso"
else
    print_message "Docker Compose já está instalado"
fi

# Configurar Firewall
print_message "Configurando Firewall (UFW)..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw allow 5432/tcp comment 'PostgreSQL'
ufw allow 6379/tcp comment 'Redis'
ufw allow 8000/tcp comment 'API Server'
ufw --force enable
print_success "Firewall configurado com sucesso"

# Configurar fail2ban
print_message "Configurando fail2ban..."
cat > /etc/fail2ban/jail.local << EOL
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 5
EOL
systemctl restart fail2ban
print_success "fail2ban configurado com sucesso"

# Verificar se o arquivo de configuração do Nginx existe
if [ ! -f "$NGINX_DIR/conf/default.conf" ]; then
    print_message "Criando configuração padrão do Nginx..."
    cat > "$NGINX_DIR/conf/default.conf" << EOL
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirecionar HTTP para HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}

# O servidor HTTPS será configurado após a geração dos certificados SSL
EOL
    print_success "Configuração padrão do Nginx criada com sucesso"
else
    print_message "Configuração do Nginx já existe"
fi

# Verificar se o certificado SSL existe e gerar se necessário
print_message "Verificando certificado SSL..."
if [ ! -d "$NGINX_DIR/ssl/live/$DOMAIN" ]; then
    print_warning "Certificado SSL não encontrado. Você tem duas opções:"
    print_message "1. Executar manualmente: certbot certonly --nginx -d $DOMAIN"
    print_message "2. Usar certificados auto-assinados para desenvolvimento/teste"
    
    read -p "Deseja gerar certificados auto-assinados para teste? (S/N): " GENERATE_SELF_SIGNED
    
    if [[ "$GENERATE_SELF_SIGNED" =~ ^[Ss]$ ]]; then
        print_message "Gerando certificados auto-assinados..."
        mkdir -p "$NGINX_DIR/ssl/live/$DOMAIN"
        
        # Gerar chave privada e certificado auto-assinado
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$NGINX_DIR/ssl/live/$DOMAIN/privkey.pem" \
            -out "$NGINX_DIR/ssl/live/$DOMAIN/fullchain.pem" \
            -subj "/CN=$DOMAIN/O=CCONTROL-M/C=BR"
        
        # Criar chain.pem (mesmo que fullchain.pem para certificados auto-assinados)
        cp "$NGINX_DIR/ssl/live/$DOMAIN/fullchain.pem" "$NGINX_DIR/ssl/live/$DOMAIN/chain.pem"
        
        print_success "Certificados auto-assinados gerados com sucesso"
        print_warning "Estes certificados são apenas para teste. Em produção, use certificados reais."
    else
        print_warning "Certificados SSL não foram configurados. Configure-os manualmente antes de iniciar."
    fi
else
    print_success "Certificados SSL encontrados"
fi

# Criar arquivo .env para variáveis de ambiente do Docker Compose
print_message "Criando arquivo .env para o Docker Compose..."
cat > "$INSTALL_DIR/.env" << EOL
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_DB=$DB_NAME
REDIS_PASSWORD=$REDIS_PASS
EOL
print_success "Arquivo .env criado com sucesso"

# Verificar se o script de inicialização do banco de dados existe
if [ ! -f "$INSTALL_DIR/init-scripts/01-init.sql" ]; then
    print_warning "Script de inicialização do banco de dados não encontrado. Crie-o manualmente."
fi

# Configurar cron para backups automáticos
print_message "Configurando backups automáticos..."
if [ -f "$INSTALL_DIR/scripts/backup.sh" ]; then
    chmod +x "$INSTALL_DIR/scripts/backup.sh"
    # Backup diário às 2 da manhã
    (crontab -l 2>/dev/null || echo "") | grep -v "backup.sh" | { cat; echo "0 2 * * * $INSTALL_DIR/scripts/backup.sh"; } | crontab -
    print_success "Backups automáticos configurados com sucesso"
else
    print_warning "Script de backup não encontrado. Crie-o manualmente."
fi

# Permitir que scripts de produção sejam executáveis
print_message "Configurando permissões para scripts..."
if [ -f "$BACKEND_DIR/start_prod.sh" ]; then
    chmod +x "$BACKEND_DIR/start_prod.sh"
    print_success "Script start_prod.sh configurado como executável"
else
    print_warning "Script start_prod.sh não encontrado"
fi

# Informações sobre como iniciar o sistema
print_message "Configuração concluída! Agora você pode:"
print_message "1. Editar o arquivo $BACKEND_DIR/.env.prod conforme necessário"
print_message "2. Iniciar o sistema com: cd $INSTALL_DIR && docker-compose -f docker-compose.prod.yml up -d"
print_message "3. Para verificar logs: docker-compose -f docker-compose.prod.yml logs -f"

print_success "Configuração do ambiente de produção concluída com sucesso!"

exit 0 