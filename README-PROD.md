# CCONTROL-M - Guia de Produção

## Visão Geral

Este documento fornece as instruções necessárias para a configuração, implantação e manutenção do CCONTROL-M em ambiente de produção. O sistema foi projetado para operar em contêineres Docker para facilitar a implantação e garantir a consistência do ambiente.

## Requisitos de Sistema

- Sistema operacional Linux (Ubuntu 20.04 LTS ou superior recomendado)
- Docker Engine v20.10 ou superior
- Docker Compose v2.0 ou superior
- Mínimo de 2GB de RAM (4GB recomendado)
- Mínimo de 20GB de espaço em disco (50GB recomendado)
- Conexão com a Internet para implantação inicial
- Domínio configurado com registros DNS apontando para o servidor (para SSL)

## Estrutura de Diretórios

```
/opt/ccontrol-m/
├── backend/               # Código da aplicação backend
├── init-scripts/          # Scripts de inicialização do banco de dados
├── nginx/                 # Configurações do Nginx
│   ├── conf/              # Arquivos de configuração
│   ├── ssl/               # Certificados SSL
│   └── logs/              # Logs do Nginx
├── logs/                  # Logs do sistema
├── backups/               # Backups do sistema
├── scripts/               # Scripts de manutenção
├── docker-compose.prod.yml # Configuração dos contêineres
└── .env                   # Variáveis de ambiente para Docker Compose
```

## Instalação Inicial

### 1. Configuração do Servidor

Execute o script de configuração para preparar o servidor:

```bash
sudo ./scripts/setup-production.sh
```

Este script irá:
- Instalar as dependências necessárias
- Configurar o firewall
- Criar a estrutura de diretórios
- Configurar o fail2ban para proteção contra ataques
- Preparar o ambiente para os certificados SSL

### 2. Configuração do Domínio e SSL

Para configurar o SSL com Let's Encrypt:

```bash
sudo certbot certonly --nginx -d ccontrol-m.seudominio.com.br
```

Copie os certificados para o diretório do Nginx:

```bash
mkdir -p /opt/ccontrol-m/nginx/ssl/live/ccontrol-m.seudominio.com.br/
cp /etc/letsencrypt/live/ccontrol-m.seudominio.com.br/* /opt/ccontrol-m/nginx/ssl/live/ccontrol-m.seudominio.com.br/
```

### 3. Configuração das Variáveis de Ambiente

Edite o arquivo `.env.prod` no diretório `backend`:

```bash
nano /opt/ccontrol-m/backend/.env.prod
```

Ajuste os seguintes parâmetros:
- `SECRET_KEY`: Gere uma chave segura com `openssl rand -hex 32`
- `DATABASE_URL`: Configure a conexão com o banco de dados
- `ALLOWED_HOSTS`: Adicione seu domínio
- Outras configurações específicas da sua instalação

### 4. Implantação dos Contêineres

Inicie os contêineres com Docker Compose:

```bash
cd /opt/ccontrol-m
docker-compose -f docker-compose.prod.yml up -d
```

Verifique se todos os contêineres estão em execução:

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 5. Verificação da Instalação

Verifique os logs para garantir que tudo está funcionando corretamente:

```bash
docker-compose -f docker-compose.prod.yml logs
```

Acesse a API através do seu domínio:
```
https://ccontrol-m.seudominio.com.br/api/v1/docs
```

## Manutenção

### Backups

Os backups são configurados para execução automática diária às 02:00. Você pode verificar os backups disponíveis em:
```
/opt/ccontrol-m/backups/
```

Para realizar um backup manual:
```bash
sudo /opt/ccontrol-m/scripts/backup.sh
```

### Restauração a partir de um Backup

Para restaurar o sistema a partir de um backup:
```bash
sudo /opt/ccontrol-m/scripts/restore.sh nome_do_arquivo_de_backup.tar.gz
```

### Atualização do Sistema

Para atualizar o sistema para uma nova versão:

1. Pare os serviços:
```bash
cd /opt/ccontrol-m
docker-compose -f docker-compose.prod.yml down
```

2. Faça backup do sistema:
```bash
sudo /opt/ccontrol-m/scripts/backup.sh
```

3. Atualize o código fonte (via git ou outro método):
```bash
git pull
```

4. Reconstrua e inicie os contêineres:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

5. Execute as migrações do banco de dados:
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Monitoramento

Você pode monitorar o sistema através dos logs:

```bash
# Visualizar logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Verificar status dos contêineres
docker-compose -f docker-compose.prod.yml ps

# Verificar uso de recursos
docker stats
```

### Resolução de Problemas

#### Verificação de Status

```bash
# Verificar se a API está respondendo
curl -I https://ccontrol-m.seudominio.com.br/health

# Verificar se o banco de dados está acessível
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U postgres
```

#### Reinicialização de Serviços

```bash
# Reiniciar todos os serviços
docker-compose -f docker-compose.prod.yml restart

# Reiniciar um serviço específico
docker-compose -f docker-compose.prod.yml restart backend
```

#### Logs de Erro

```bash
# Verificar logs do backend
docker-compose -f docker-compose.prod.yml logs backend

# Verificar logs do Nginx
cat /opt/ccontrol-m/nginx/logs/error.log
```

## Segurança

### Renovação de Certificados SSL

Os certificados Let's Encrypt expiram após 90 dias. Configure um cron job para renovação automática:

```bash
# Adicionar ao crontab
sudo crontab -e

# Adicionar a seguinte linha
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/ccontrol-m.seudominio.com.br/* /opt/ccontrol-m/nginx/ssl/live/ccontrol-m.seudominio.com.br/ && docker-compose -f /opt/ccontrol-m/docker-compose.prod.yml restart nginx
```

### Firewall e Segurança

O firewall (UFW) é configurado automaticamente pelo script de configuração. Para verificar seu status:

```bash
sudo ufw status
```

Para adicionar uma nova regra:

```bash
sudo ufw allow <porta>/tcp
```

### Atualizações de Segurança

Mantenha o sistema operacional e os pacotes atualizados:

```bash
sudo apt update && sudo apt upgrade -y
```

Mantenha as imagens Docker atualizadas:

```bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Configurações Avançadas

### Escalonamento

Para aumentar o número de workers do backend:

```bash
# Editar o arquivo .env
nano /opt/ccontrol-m/.env

# Adicionar ou modificar a variável WORKERS
WORKERS=8

# Reiniciar o serviço backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Otimização do Banco de Dados

Execute regularmente a otimização do banco de dados:

```bash
docker-compose -f docker-compose.prod.yml exec postgres vacuumdb -U postgres --all --analyze
```

### Balanceamento de Carga (para implantações maiores)

Para configurar um balanceador de carga com múltiplas instâncias, consulte a documentação avançada ou entre em contato com o suporte.

## Suporte

Para suporte técnico, entre em contato com:
- Email: suporte@seudominio.com.br
- Telefone: (XX) XXXX-XXXX

## Licença

CCONTROL-M é um software proprietário. Todos os direitos reservados. 