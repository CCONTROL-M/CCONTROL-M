### ESTÁGIO DE BUILD ###
FROM node:18-alpine as build

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de package primeiro para aproveitar o cache
COPY package.json package-lock.json ./

# Instalar dependências
RUN npm ci

# Copiar o resto do código
COPY . .

# Definir variáveis de ambiente para a build
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_MOCK_ENABLED=false
ENV NODE_ENV=production

# Construir a aplicação
RUN npm run build

### ESTÁGIO DE PRODUÇÃO ###
FROM nginx:alpine

# Remover a configuração padrão do Nginx
RUN rm -rf /usr/share/nginx/html/*
RUN rm /etc/nginx/conf.d/default.conf

# Copiar arquivos de build do estágio anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuração personalizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Porta a ser exposta
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"] 