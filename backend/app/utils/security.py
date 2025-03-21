"""Utilitários para segurança e criptografia."""
import secrets
from passlib.context import CryptContext

# Configuração do contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto simples corresponde ao hash armazenado.
    
    Args:
        plain_password: Senha em texto simples a verificar
        hashed_password: Hash da senha armazenada
        
    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera um hash bcrypt para a senha fornecida.
    
    Args:
        password: Senha em texto simples
        
    Returns:
        str: Hash bcrypt da senha
    """
    return pwd_context.hash(password)


def generate_random_string(length: int = 32) -> str:
    """
    Gera uma string aleatória segura para uso em tokens, chaves, etc.
    
    Args:
        length: Comprimento da string aleatória
        
    Returns:
        str: String aleatória segura
    """
    return secrets.token_urlsafe(length) 