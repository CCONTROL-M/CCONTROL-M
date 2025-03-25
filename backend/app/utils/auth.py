"""Utilitários de autenticação para a API."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Função simulada para obter usuário atual
async def obter_usuario_atual(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token"))):
    """
    Retorna o usuário autenticado com base no token JWT.
    
    Esta é uma versão simplificada para desenvolvimento que não verifica
    tokens reais. Em produção, seria substituída por uma implementação
    completa com validação JWT.
    
    Args:
        token: Token JWT obtido do header de autorização
        
    Returns:
        Objeto com informações do usuário simulado
    """
    # Usuário simulado para desenvolvimento
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "nome": "Usuário de Teste",
        "email": "usuario@teste.com",
        "perfil": "admin",
        "empresa_id": "11111111-1111-1111-1111-111111111111"
    } 