FROM python:3.11-slim

LABEL maintainer="CCONTROL-M <contato@ccontrol-m.com.br>"
LABEL description="API Backend para CCONTROL-M - Sistema de Controle Financeiro e Gestão"

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    curl \
    procps \
    netcat-openbsd \
    htop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN groupadd -r ccontrol && useradd -r -g ccontrol ccontrol

# Criar diretórios necessários
RUN mkdir -p /app/logs /app/uploads /app/static
WORKDIR /app

# Copiar requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# Copiar o código da aplicação
COPY . .

# Configurar permissões para os diretórios
RUN chown -R ccontrol:ccontrol /app && \
    chmod +x /app/start_prod.sh

# Expor a porta da aplicação
EXPOSE 8000

# Mudar para o usuário não-root
USER ccontrol

# Verificar se todas as dependências foram instaladas corretamente
RUN python -c "import pkg_resources; pkg_resources.require(open('requirements.txt', 'r'))"

# Script de entrada
ENTRYPOINT ["/app/start_prod.sh"] 