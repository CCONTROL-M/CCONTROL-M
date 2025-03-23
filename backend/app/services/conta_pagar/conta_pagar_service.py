"""Serviço principal para gerenciamento de contas a pagar no sistema CCONTROL-M."""
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


class ContaPagarService:
    """Serviço para gerenciamento de contas a pagar."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_async_session),
        auditoria_service: AuditoriaService = Depends()
    ):
        """Inicializar serviço com dependências necessárias."""
        self.repository = ContaPagarRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logging.getLogger(__name__)

    async def create(
        self,
        conta: ContaPagarCreate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> ContaPagar:
        """
        Criar uma nova conta a pagar.

        Parameters:
            conta: Dados da conta a pagar
            usuario_id: ID do usuário que está criando a conta
            empresa_id: ID da empresa à qual a conta pertence

        Returns:
            Conta a pagar criada
        """
        # Verificar se a empresa da conta corresponde à empresa do usuário
        if conta.id_empresa != empresa_id:
            self.logger.warning(
                f"Tentativa de criar conta para empresa inválida: {conta.id_empresa} vs {empresa_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A conta deve pertencer à empresa do usuário logado"
            )

        # Criar conta no repositório
        try:
            created_conta = await self.repository.create(conta)
            
            # Registrar ação de auditoria
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                empresa_id=empresa_id,
                acao="CRIAR",
                entidade="ContaPagar",
                entidade_id=str(created_conta.id),
                descricao=f"Criação de conta a pagar: {created_conta.descricao}"
            )
            
            return created_conta
        except Exception as e:
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

        Parameters:
            id_conta: ID da conta a pagar a ser atualizada
            conta: Dados atualizados da conta a pagar
            usuario_id: ID do usuário que está atualizando a conta
            empresa_id: ID da empresa à qual a conta pertence

        Returns:
            Conta a pagar atualizada
        """
        # Verificar se a conta existe e pertence à empresa
        existing_conta = await self.get_by_id(id_conta, empresa_id)
        if not existing_conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a pagar não encontrada"
            )

        # Atualizar conta no repositório
        try:
            updated_conta = await self.repository.update(id_conta, conta, empresa_id)
            
            # Registrar ação de auditoria
            changes = []
            for field, value in conta.__dict__.items():
                if value is not None and field != "id_empresa":
                    changes.append(f"{field}: {value}")
            
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                empresa_id=empresa_id,
                acao="ATUALIZAR",
                entidade="ContaPagar",
                entidade_id=str(id_conta),
                descricao=f"Atualização de conta a pagar: {', '.join(changes)}"
            )
            
            return updated_conta
        except Exception as e:
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
        Excluir uma conta a pagar.

        Parameters:
            id_conta: ID da conta a pagar a ser excluída
            usuario_id: ID do usuário que está excluindo a conta
            empresa_id: ID da empresa à qual a conta pertence

        Returns:
            Mensagem de confirmação
        """
        # Verificar se a conta existe e pertence à empresa
        existing_conta = await self.get_by_id(id_conta, empresa_id)
        if not existing_conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conta a pagar não encontrada"
            )

        # Verificar se a conta já foi paga
        if existing_conta.status == StatusContaPagar.pago:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível excluir uma conta que já foi paga"
            )

        # Excluir conta no repositório
        try:
            await self.repository.delete(id_conta, empresa_id)
            
            # Registrar ação de auditoria
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                empresa_id=empresa_id,
                acao="EXCLUIR",
                entidade="ContaPagar",
                entidade_id=str(id_conta),
                descricao=f"Exclusão de conta a pagar: {existing_conta.descricao}"
            )
            
            return {"message": "Conta a pagar excluída com sucesso"}
        except Exception as e:
            self.logger.error(f"Erro ao excluir conta a pagar: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir conta a pagar: {str(e)}"
            )

    async def get_by_id(
        self,
        id_conta: UUID,
        empresa_id: UUID
    ) -> ContaPagar:
        """
        Buscar uma conta a pagar pelo ID.

        Parameters:
            id_conta: ID da conta a pagar a ser buscada
            empresa_id: ID da empresa à qual a conta pertence

        Returns:
            Conta a pagar encontrada
        """
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
        Buscar contas a pagar com filtros e paginação.

        Parameters:
            empresa_id: ID da empresa
            skip: Número de registros para pular (para paginação)
            limit: Número máximo de registros a retornar
            status: Filtro por status da conta
            data_inicial: Filtro por data inicial de vencimento
            data_final: Filtro por data final de vencimento
            fornecedor_id: Filtro por fornecedor
            categoria_id: Filtro por categoria
            busca: Busca textual na descrição da conta

        Returns:
            Lista paginada de contas a pagar
        """
        return await self.repository.get_multi(
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
        
    async def registrar_pagamento(
        self,
        id_conta: UUID,
        data_pagamento: date,
        valor_pago: float,
        empresa_id: UUID,
        usuario_id: UUID,
        observacoes: Optional[str] = None
    ) -> ContaPagar:
        """
        Registrar o pagamento de uma conta.
        
        Parameters:
            id_conta: ID da conta a pagar
            data_pagamento: Data em que o pagamento foi realizado
            valor_pago: Valor pago
            empresa_id: ID da empresa
            usuario_id: ID do usuário que registrou o pagamento
            observacoes: Observações sobre o pagamento
            
        Returns:
            Conta atualizada com o pagamento registrado
        """
        # Verificar se a conta existe e pertence à empresa
        conta = await self.get_by_id(id_conta, empresa_id)
        
        # Verificar se a conta já está paga
        if conta.status == StatusContaPagar.pago:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta conta já foi paga"
            )
            
        # Verificar se a conta está cancelada
        if conta.status == StatusContaPagar.cancelado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível pagar uma conta cancelada"
            )
            
        # Calcular status baseado no valor pago
        novo_status = StatusContaPagar.pago
        if valor_pago < float(conta.valor):
            novo_status = StatusContaPagar.parcial
            
        # Atualizar conta
        update_data = ContaPagarUpdate(
            status=novo_status,
            data_pagamento=data_pagamento,
            valor_pago=valor_pago,
            observacoes=observacoes
        )
        
        conta_atualizada = await self.update(id_conta, update_data, usuario_id, empresa_id)
        
        # Registrar ação específica de pagamento
        await self.auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            acao="PAGAR",
            entidade="ContaPagar",
            entidade_id=str(id_conta),
            descricao=f"Pagamento de conta: {conta.descricao}. Valor: {valor_pago}"
        )
        
        return conta_atualizada
        
    async def cancelar_conta(
        self,
        id_conta: UUID,
        motivo_cancelamento: str,
        empresa_id: UUID,
        usuario_id: UUID,
        observacoes: Optional[str] = None
    ) -> ContaPagar:
        """
        Cancelar uma conta a pagar.
        
        Parameters:
            id_conta: ID da conta a pagar
            motivo_cancelamento: Motivo do cancelamento
            empresa_id: ID da empresa
            usuario_id: ID do usuário que cancelou a conta
            observacoes: Observações adicionais
            
        Returns:
            Conta atualizada com status cancelado
        """
        # Verificar se a conta existe e pertence à empresa
        conta = await self.get_by_id(id_conta, empresa_id)
        
        # Verificar se a conta já está paga
        if conta.status == StatusContaPagar.pago:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível cancelar uma conta que já foi paga"
            )
            
        # Verificar se a conta já está cancelada
        if conta.status == StatusContaPagar.cancelado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta conta já está cancelada"
            )
            
        # Preparar observações
        nova_observacao = f"CANCELADO: {motivo_cancelamento}"
        if observacoes:
            nova_observacao += f"\n{observacoes}"
        if conta.observacoes:
            nova_observacao += f"\n\nObservações anteriores: {conta.observacoes}"
            
        # Atualizar conta
        update_data = ContaPagarUpdate(
            status=StatusContaPagar.cancelado,
            observacoes=nova_observacao
        )
        
        conta_atualizada = await self.update(id_conta, update_data, usuario_id, empresa_id)
        
        # Registrar ação específica de cancelamento
        await self.auditoria_service.registrar_acao(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            acao="CANCELAR",
            entidade="ContaPagar",
            entidade_id=str(id_conta),
            descricao=f"Cancelamento de conta: {conta.descricao}. Motivo: {motivo_cancelamento}"
        )
        
        return conta_atualizada
