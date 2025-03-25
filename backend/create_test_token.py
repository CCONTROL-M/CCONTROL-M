import jwt
import datetime
import uuid
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(".env")

# Obter a chave secreta das variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-for-development-only")

# ID de empresa para testes - usando o mesmo ID configurado no frontend
EMPRESA_ID = "11111111-1111-1111-1111-111111111111"
USER_ID = str(uuid.uuid4())

# Dados para o payload do token
payload = {
    "id_usuario": USER_ID,
    "id_empresa": EMPRESA_ID,
    "nome": "Usuário de Teste",
    "email": "teste@example.com",
    "tipo_usuario": "ADMIN",
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),  # Token válido por 30 dias
    "iat": datetime.datetime.utcnow()
}

# Gerar o token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

print("Token JWT gerado para testes:")
print(token)
print("\nDados do token:")
print(f"ID Usuário: {USER_ID}")
print(f"ID Empresa: {EMPRESA_ID}")
print(f"Expiração: {payload['exp']}")
print("\nInstruções:")
print("1. Abra o Console do navegador (F12) no frontend")
print("2. Execute o seguinte comando para salvar o token:")
print(f"localStorage.setItem('token', '{token}');")
print("3. Recarregue a página para usar o novo token") 