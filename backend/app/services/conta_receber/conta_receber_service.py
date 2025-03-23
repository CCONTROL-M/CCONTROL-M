"""Serviço principal para gerenciamento de contas a receber no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
import logging

from app.database import get_async_session
from app.schemas.conta_receber import ContaReceberCreate, ContaReceberUpdate, ContaReceber
from app.repositories.conta_receber_repository import ContaReceberRepository
from app.services.auditoria_service import AuditoriaService


class ContaReceberService:
    """
    Serviço principal para gerenciamento de contas a receber.
    
    Esta classe implementa a lógica de negócio para operações relacionadas a contas a receber
    no sistema CCONTROL-M.
    """
    
    def __init__(
        self, 
        session: AsyncSession = Depends(get_async_session),
        auditoria_service: AuditoriaService = Depends()
    ):
        """Inicializar serviço com repositório e dependências."""
        self.repository = ContaReceberRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logging.getLogger(__name__)
    
    async def criar_conta(
        self,
        conta_data: ContaReceberCreate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ContaReceber:
        """
        Criar uma nova conta a receber.
        
        Args:
            conta_data: Dados da conta a receber
            usuario_id: ID do usuário que está criando
            empresa_id: ID da empresa
            
        Returns:
            Conta a receber criada
        """
        try:
            # Garantir que a conta pertence à empresa correta
            conta_data.id_empresa = empresa_id
            
            # Criar conta
            nova_conta = await self.repository.create(conta_data)
            
            # Registrar ação de auditoria
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CRIAR_CONTA_RECEBER",
                detalhes={
                    "id_conta": str(nova_conta.id_conta_receber),
                    "descricao": nova_conta.descricao,
                    "valor": str(nova_conta.valor)
                },
                empresa_id=empresa_id
            )
            
            return nova_conta
            
        except Exception as e:
            self.logger.error(f"Erro ao criar conta a receber: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar conta a receber"
            )
    
    async def buscar_conta(
        self,
        id_conta: UUID,
        empresa_id: UUID
    ) -> ContaReceber:
        """
        Buscar uma conta a receber pelo ID.
        
        Args:
            id_conta: ID da conta a receber
            empresa_id: ID da empresa
            
        Returns:
            Conta a receber encontrada
        """
        try:
            # Buscar conta
            conta = await self.repository.get_by_id(id_conta)
            
            # Verificar se conta pertence à empresa
            if not conta or conta.id_empresa != empresa_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta a receber não encontrada"
                )
                
            return conta
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao buscar conta a receber: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar conta a receber"
            )
    
    async def listar_contas(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        cliente_id: Optional[UUID] = None,
        data_inicial: Optional[str] = None,
        data_final: Optional[str] = None
    ) -> List[ContaReceber]:
        """
        Listar contas a receber com filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Registros para pular
            limit: Limite de registros
            status: Filtro por status
            cliente_id: Filtro por cliente
            data_inicial: Filtro por data inicial
            data_final: Filtro por data final
            
        Returns:
            Lista de contas a receber
        """
        try:
            # Construir filtros
            filtros = {
                "id_empresa": empresa_id
            }
            
            if status:
                filtros["status"] = status
                
            if cliente_id:
                filtros["id_cliente"] = cliente_id
            
            # Buscar contas
            return await self.repository.get_multi(
                skip=skip,
                limit=limit,
                filtros=filtros,
                data_inicial=data_inicial,
                data_final=data_final
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao listar contas a receber: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao listar contas a receber"
            )
    
    async def atualizar_conta(
        self,
        id_conta: UUID,
        conta_data: ContaReceberUpdate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ContaReceber:
        """
        Atualizar uma conta a receber.
        
        Args:
            id_conta: ID da conta a receber
            conta_data: Dados a atualizar
            usuario_id: ID do usuário que está atualizando
            empresa_id: ID da empresa
            
        Returns:
            Conta a receber atualizada
        """
        try:
            # Verificar se conta existe e pertence à empresa
            conta_atual = await self.buscar_conta(id_conta, empresa_id)
            
            # Atualizar conta
            conta_atualizada = await self.repository.update(
                id_conta,
                conta_data
            )
            
            # Registrar ação de auditoria
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_CONTA_RECEBER",
                detalhes={
                    "id_conta": str(id_conta),
                    "alteracoes": conta_data.model_dump(exclude_unset=True)
                },
                empresa_id=empresa_id
            )
            
            return conta_atualizada
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao atualizar conta a receber: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar conta a receber"
            )
    
    async def excluir_conta(
        self,
        id_conta: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> None:
        """
        Excluir uma conta a receber.
        
        Args:
            id_conta: ID da conta a receber
            usuario_id: ID do usuário que está excluindo
            empresa_id: ID da empresa
        """
        try:
            # Verificar se conta existe e pertence à empresa
            conta = await self.buscar_conta(id_conta, empresa_id)
            
            # Excluir conta
            await self.repository.delete(id_conta)
            
            # Registrar ação de auditoria
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="EXCLUIR_CONTA_RECEBER",
                detalhes={
                    "id_conta": str(id_conta),
                    "descricao": conta.descricao,
                    "valor": str(conta.valor)
                },
                empresa_id=empresa_id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao excluir conta a receber: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao excluir conta a receber"
            ) 