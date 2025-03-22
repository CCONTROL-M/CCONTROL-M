"""
Módulo para verificação de permissões no sistema CCONTROL-M.

Este módulo contém funções para verificar se um usuário tem permissão para acessar
determinados recursos ou realizar determinadas ações no sistema.
"""
from typing import Any, Dict
from uuid import UUID
from fastapi import HTTPException, status, Depends
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.schemas.token import TokenPayload
from app.repositories.permissao_usuario_repository import PermissaoUsuarioRepository
from app.database import get_async_session


async def verify_permission(user: Dict[str, Any], permission: str, id_empresa: UUID) -> bool:
    """
    Verifica se o usuário tem permissão para executar uma determinada ação.
    
    Args:
        user: Dados do usuário autenticado (from TokenPayload)
        permission: Permissão necessária no formato "recurso:acao"
        id_empresa: ID da empresa para validação de acesso
        
    Returns:
        bool: True se o usuário tem permissão
        
    Raises:
        HTTPException: Se o usuário não tiver permissão
    """
    # Se o usuário for administrador, tem todas as permissões
    if user.get("tipo_usuario") == "ADMIN":
        return True
        
    # Verificar se o usuário pertence à empresa
    empresa_id_token = str(user.get("empresa_id", "")).lower()
    empresa_id_acesso = str(id_empresa).lower()
    
    if empresa_id_token != empresa_id_acesso:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar dados de outra empresa"
        )
    
    # Verificar permissões específicas do usuário
    if ":" in permission:
        recurso, acao = permission.split(":", 1)
        
        # Usar o repositório para verificar permissões no banco de dados
        permissao_repo = PermissaoUsuarioRepository()
        has_permission = await permissao_repo.check_user_permission(
            user_id=user.get("sub"),
            recurso=recurso,
            acao=acao,
            tenant_id=id_empresa
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sem permissão para '{acao}' no recurso '{recurso}'"
            )
    
    return True


def require_permission(recurso: str, acao: str):
    """
    Decorator para verificar permissão de acesso a um recurso e ação específica.
    
    Args:
        recurso: Nome do recurso (ex: "clientes", "vendas")
        acao: Ação necessária (ex: "criar", "listar", "editar", "deletar")
        
    Returns:
        Callable: Função de dependência que verifica a permissão
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args,
            current_user: TokenPayload = Depends(get_current_user),
            session: AsyncSession = Depends(get_async_session),
            **kwargs
        ):
            # Se o usuário for administrador, tem todas as permissões
            if current_user.tipo_usuario == "ADMIN":
                return await func(*args, current_user=current_user, session=session, **kwargs)
                
            # Obter ID da empresa (pode vir dos parâmetros ou do token)
            id_empresa = kwargs.get("id_empresa")
            if not id_empresa:
                id_empresa = current_user.empresa_id
                
            # Verificar permissão específica
            permissao_repo = PermissaoUsuarioRepository()
            has_permission = await permissao_repo.check_user_permission(
                user_id=current_user.sub,
                recurso=recurso,
                acao=acao,
                tenant_id=id_empresa
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Sem permissão para '{acao}' no recurso '{recurso}'"
                )
                
            return await func(*args, current_user=current_user, session=session, **kwargs)
            
        return wrapper
    return decorator 