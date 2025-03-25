# Configuração de Produção - Frontend CCONTROL-M

Este documento explica como configurar e executar o frontend do CCONTROL-M em ambiente de produção.

## Requisitos

- Node.js 16+ 
- npm 7+
- Acesso ao servidor da API

## Arquivos de Configuração

### 1. Arquivo .env.production

O arquivo `.env.production` contém as configurações específicas para o ambiente de produção:

```
# URL da API (Backend) - Ajuste conforme seu ambiente de produção
VITE_API_URL=http://localhost:8000

# Desativar modo mock em produção
VITE_MOCK_ENABLED=false

# Desativar logs de desenvolvimento
VITE_ENABLE_DEBUG_LOGS=false
```

> **Importante**: Substitua `http://localhost:8000` pelo endereço real do seu servidor de API em produção.

## Compilação para Produção

Para compilar o projeto para produção, execute:

```bash
npm run build:prod
```

Este comando irá:
1. Verificar erros de TypeScript
2. Remover console.logs e debuggers
3. Minimizar o código
4. Otimizar as imagens
5. Dividir o código em chunks para melhor carregamento

O resultado da compilação será gerado na pasta `dist/`.

## Deploy em Produção

Execute o script de deploy completo (que inclui linting, testes e build de produção):

```bash
npm run deploy
```

## Servidor para Produção

Para servir a aplicação em produção usando o Vite Preview (apenas para testes):

```bash
npm run start:prod
```

Este comando iniciará um servidor na porta 5000 e permitirá acesso externo.

## Para Produção Real

Em um ambiente de produção real, recomendamos:

1. Utilizar um servidor web como Nginx ou Apache
2. Configurar HTTPS
3. Implementar cache e compressão

### Exemplo de Configuração Nginx

```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    # Redirecionar HTTP para HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name seu-dominio.com;
    
    ssl_certificate /caminho/para/certificado.crt;
    ssl_certificate_key /caminho/para/chave.key;
    
    # Configurações de SSL seguras
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    
    # Diretório com os arquivos compilados
    root /caminho/para/dist;
    
    # Configuração de cache para arquivos estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    # Configuração para o SPA - redireciona todas as rotas para index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy para API (opcional se estiver no mesmo servidor)
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Docker (Opcional)

Se preferir usar Docker, crie um `Dockerfile` na raiz do projeto:

```dockerfile
# Estágio de build
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build:prod

# Estágio de produção com Nginx
FROM nginx:stable-alpine

# Copiar configuração personalizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar arquivos de build
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

E crie um arquivo `nginx.conf`:

```
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Configuração para o proxy da API se necessário
    location /api/ {
        proxy_pass http://api-service:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Para construir e executar o container:

```bash
docker build -t ccontrol-m-frontend .
docker run -p 80:80 ccontrol-m-frontend
```

## Segurança em Produção

1. Todas as chamadas de API usam HTTPS
2. Modo Mock é desativado em produção
3. Logs de depuração são removidos
4. Mensagens de erro sensíveis são ocultadas

## Monitoramento e Diagnóstico

Para monitoramento em produção, considere integrar:

1. Google Analytics ou Matomo para métricas de usuário
2. Sentry.io para rastreamento de erros
3. Prometheus/Grafana para métricas de servidor 