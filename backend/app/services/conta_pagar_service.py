"""Serviço para gerenciamento de contas a pagar."""
import logging
from uuid import UUID
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.repositories.conta_pagar_repository import ContaPagarRepository
from app.schemas.conta_pagar import (
    ContaPagarCreate,
    ContaPagarUpdate,
    ContaPagar,
    StatusContaPagar
)
from app.services.auditoria_service import AuditoriaService
from app.schemas.pagination import PaginatedResponse

logger = logging.getLogger(__name__)


class ContaPagarService:
    """Serviço para gerenciamento de contas a pagar."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_async_session),
        auditoria_service: AuditoriaService = Depends()
    ):
        """Inicializa o serviço com a sessão do banco de dados."""
        self.repository = ContaPagarRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logger

    async def create(
        self,
        conta: ContaPagarCreate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ContaPagar:
        """
        Criar uma nova conta a pagar.
        
        Args:
            conta: Dados da conta a pagar
            usuario_id: ID do usuário que está criando
            empresa_id: ID da empresa
            
        Returns:
            Conta a pagar criada
            
        Raises:
            HTTPException: Em caso de erro na validação ou criação
        """
        self.logger.info(f"Criando conta a pagar: {conta.descricao}")
        
        try:
            # Criar conta
            nova_conta = await self.repository.create(conta, empresa_id)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CRIAR_CONTA_PAGAR",
                detalhes={
                    "id_conta": str(nova_conta.id_conta),
                    "descricao": nova_conta.descricao,
                    "valor": str(nova_conta.valor),
                    "data_vencimento": nova_conta.data_vencimento.isoformat(),
                    "status": nova_conta.status
                },
                empresa_id=empresa_id
            )
            
            # Comitar alterações
            await self.repository.commit()
            
            return nova_conta
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao criar conta a pagar: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar conta a pagar: {str(e)}"
            )

    async def update(
        self,
        id_conta: UUID,
        conta: ContaPagarUpdate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ContaPagar:
        """
        Atualizar uma conta a pagar existente.
        
        Args:
            id_conta: ID da conta a pagar
            conta: Dados para atualização
            usuario_id: ID do usuário que está atualizando
            empresa_id: ID da empresa
            
        Returns:
            Conta a pagar atualizada
            
        Raises:
            HTTPException: Em caso de erro na validação ou atualização
        """
        self.logger.info(f"Atualizando conta a pagar: {id_conta}")
        
        try:
            # Verificar se a conta existe
            conta_atual = await self.repository.get_by_id(id_conta, empresa_id)
            if not conta_atual:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta a pagar não encontrada"
                )
            
            # Atualizar conta
            conta_atualizada = await self.repository.update(id_conta, conta, empresa_id)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_CONTA_PAGAR",
                detalhes={
                    "id_conta": str(id_conta),
                    "alteracoes": conta.model_dump(exclude_unset=True),
                    "status_anterior": conta_atual.status,
                    "status_novo": conta_atualizada.status
                },
                empresa_id=empresa_id
            )
            
            # Comitar alterações
            await self.repository.commit()
            
            return conta_atualizada
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao atualizar conta a pagar: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar conta a pagar: {str(e)}"
            )

    async def delete(
        self,
        id_conta: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> Dict[str, str]:
        """
        Remover uma conta a pagar.
        
        Args:
            id_conta: ID da conta a pagar
            usuario_id: ID do usuário que está removendo
            empresa_id: ID da empresa
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Em caso de erro na validação ou remoção
        """
        self.logger.info(f"Removendo conta a pagar: {id_conta}")
        
        try:
            # Verificar se a conta existe
            conta = await self.repository.get_by_id(id_conta, empresa_id)
            if not conta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta a pagar não encontrada"
                )
            
            # Remover conta
            await self.repository.delete(id_conta, empresa_id)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="EXCLUIR_CONTA_PAGAR",
                detalhes={
                    "id_conta": str(id_conta),
                    "descricao": conta.descricao,
                    "valor": str(conta.valor),
                    "status": conta.status
                },
                empresa_id=empresa_id
            )
            
            # Comitar alterações
            await self.repository.commit()
            
            return {"mensagem": "Conta a pagar removida com sucesso"}
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao remover conta a pagar: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover conta a pagar: {str(e)}"
            )

    async def get_by_id(
        self,
        id_conta: UUID,
        empresa_id: UUID
    ) -> ContaPagar:
        """
        Buscar uma conta a pagar pelo ID.
        
        Args:
            id_conta: ID da conta a pagar
            empresa_id: ID da empresa
            
        Returns:
            Conta a pagar encontrada
            
        Raises:
            HTTPException: Se a conta não for encontrada
        """
        self.logger.info(f"Buscando conta a pagar: {id_conta}")
        
        conta = await self.repository.get_by_id(id_conta, empresa_id)
        if not conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a pagar não encontrada"
            )
        
        return conta

    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusContaPagar] = None,
        data_inicial: Optional[date] = None,
        data_final: Optional[date] = None,
        fornecedor_id: Optional[UUID] = None,
        categoria_id: Optional[UUID] = None,
        busca: Optional[str] = None
    ) -> PaginatedResponse[ContaPagar]:
        """
        Buscar múltiplas contas a pagar com filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            status: Filtrar por status
            data_inicial: Data inicial para filtro
            data_final: Data final para filtro
            fornecedor_id: Filtrar por fornecedor
            categoria_id: Filtrar por categoria
            busca: Termo para busca
            
        Returns:
            Lista paginada de contas a pagar
        """
        try:
            contas, total = await self.repository.get_multi(
                empresa_id=empresa_id,
                skip=skip,
                limit=limit,
                status=status,
                data_inicial=data_inicial,
                data_final=data_final,
                fornecedor_id=fornecedor_id,
                categoria_id=categoria_id,
                busca=busca
            )
            
            return PaginatedResponse(
                items=contas,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 1
            )
        except Exception as e:
            self.logger.error(f"Erro ao buscar contas a pagar: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar contas a pagar"
            ) 