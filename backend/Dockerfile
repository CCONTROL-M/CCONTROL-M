FROM python:3.9-slim

WORKDIR /app

# Copiar arquivos de requisitos primeiro e instalar
# Isso aproveita o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Porta a ser exposta
EXPOSE 8002

# Criar diretórios necessários se não existirem
RUN mkdir -p /app/logs

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"] 