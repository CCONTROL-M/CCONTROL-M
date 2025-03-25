"""
Utilitários para verificações de permissões e autorizações.
"""
import logging
from typing import Optional, Any
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Configuração de logger
logger = logging.getLogger(__name__)

async def verificar_permissao_empresa(
    id_empresa: UUID,
    current_user: Any,
    session: AsyncSession,
    admin_only: bool = False
) -> dict:
    """
    Verifica se o usuário atual tem permissão para acessar dados da empresa especificada.
    
    Args:
        id_empresa: ID da empresa a ser verificada
        current_user: Usuário atual
        session: Sessão de banco de dados
        admin_only: Se True, apenas admins podem acessar
        
    Returns:
        dict com o ID da empresa se o usuário tiver permissão
        
    Raises:
        HTTPException: Se o usuário não tiver permissão
    """
    # Verificar se usuário tem atributo id_empresa
    if not hasattr(current_user, 'id_empresa'):
        logger.warning("Usuário sem empresa vinculada tentou acessar recurso")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário sem vínculo com empresa"
        )
    
    # Se o usuário é admin do sistema, pode acessar qualquer empresa
    is_admin = hasattr(current_user, 'tipo_usuario') and current_user.tipo_usuario == 'ADMIN'
    
    # Verificar se pertence à empresa ou é admin
    if str(current_user.id_empresa) != str(id_empresa) and not is_admin:
        logger.warning(f"Usuário com id_empresa={current_user.id_empresa} tentou acessar empresa {id_empresa}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar dados desta empresa"
        )
    
    # Verificar permissão admin_only
    if admin_only and not is_admin:
        logger.warning("Usuário sem privilégios de admin tentou acessar recurso restrito")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operação requer privilégios de administrador"
        )
    
    # Sucesso - retorna ID da empresa como string para compatibilidade
    return {"id_empresa": str(id_empresa)} 