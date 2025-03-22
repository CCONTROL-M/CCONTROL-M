"""Serviço para gerenciamento de lançamentos financeiros."""
import logging
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models.lancamento import Lancamento
from app.repositories.lancamento_repository import LancamentoRepository
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.fornecedor_repository import FornecedorRepository
from app.repositories.conta_bancaria_repository import ContaBancariaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.schemas.lancamento import (
    LancamentoCreate, LancamentoUpdate, Lancamento as LancamentoSchema, 
    StatusLancamento, TipoLancamento
)
from app.schemas.pagination import PaginatedResponse
from app.services.log_sistema_service import LogSistemaService


# Configurar logger
logger = logging.getLogger(__name__)


class LancamentoService:
    """Serviço para gerenciamento de lançamentos financeiros."""

    def __init__(self, session: AsyncSession):
        """Inicializar serviço com sessão."""
        self.session = session
        self.repository = LancamentoRepository(session)
        self.cliente_repository = ClienteRepository(session)
        self.fornecedor_repository = FornecedorRepository(session)
        self.conta_repository = ContaBancariaRepository(session)
        self.forma_pagamento_repository = FormaPagamentoRepository(session)

    async def get_lancamento(self, id_lancamento: UUID, id_empresa: UUID) -> LancamentoSchema:
        """
        Obter lançamento por ID.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa
            
        Returns:
            Lançamento encontrado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado
        """
        logger.info(f"Buscando lançamento com ID {id_lancamento}")
        
        lancamento = await self.repository.get_by_id(id_lancamento, id_empresa)
        
        if not lancamento:
            logger.warning(f"Lançamento com ID {id_lancamento} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lançamento não encontrado"
            )
            
        return LancamentoSchema.model_validate(lancamento)

    async def listar_lancamentos(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        tipo: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        id_cliente: Optional[UUID] = None,
        id_fornecedor: Optional[UUID] = None,
        id_conta: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> PaginatedResponse[LancamentoSchema]:
        """
        Listar lançamentos com filtros e paginação.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular
            limit: Limite de registros
            tipo: Filtrar por tipo (receita/despesa)
            data_inicio: Filtrar por data inicial
            data_fim: Filtrar por data final
            id_cliente: Filtrar por cliente
            id_fornecedor: Filtrar por fornecedor
            id_conta: Filtrar por conta bancária
            status: Filtrar por status
            
        Returns:
            Lista paginada de lançamentos
        """
        logger.info(f"Listando lançamentos para empresa {id_empresa}")
        
        try:
            # Verificar filtros e validar
            if id_cliente:
                cliente = await self.cliente_repository.get_by_id(id_cliente, id_empresa)
                if not cliente:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente não encontrado"
                    )
            
            if id_fornecedor:
                fornecedor = await self.fornecedor_repository.get_by_id(id_fornecedor, id_empresa)
                if not fornecedor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Fornecedor não encontrado"
                    )
            
            if id_conta:
                conta = await self.conta_repository.get_by_id(id_conta, id_empresa)
                if not conta:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conta bancária não encontrada"
                    )
            
            # Buscar lançamentos
            lancamentos, total = await self.repository.get_by_empresa(
                id_empresa=id_empresa,
                skip=skip,
                limit=limit,
                tipo=tipo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                id_cliente=id_cliente,
                id_fornecedor=id_fornecedor,
                id_conta=id_conta,
                status=status
            )
            
            # Converter para schema de resposta
            items = [LancamentoSchema.model_validate(l) for l in lancamentos]
            
            # Criar resposta paginada
            return PaginatedResponse[LancamentoSchema](
                items=items,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 1
            )
            
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro ao listar lançamentos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao listar lançamentos: {str(e)}"
            )

    async def criar_lancamento(self, lancamento_data: LancamentoCreate, id_empresa: UUID, usuario_id: UUID) -> LancamentoSchema:
        """
        Criar novo lançamento.
        
        Args:
            lancamento_data: Dados do lançamento
            id_empresa: ID da empresa
            usuario_id: ID do usuário
            
        Returns:
            Lançamento criado
            
        Raises:
            HTTPException: Se houver erro ao criar
        """
        logger.info(f"Criando novo lançamento para empresa {id_empresa}")
        
        try:
            # Verificar se o cliente existe, se fornecido
            if lancamento_data.id_cliente:
                cliente = await self.cliente_repository.get_by_id(
                    lancamento_data.id_cliente, 
                    id_empresa
                )
                if not cliente:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente não encontrado ou não pertence a esta empresa"
                    )
            
            # Verificar se o fornecedor existe, se fornecido
            if lancamento_data.id_fornecedor:
                fornecedor = await self.fornecedor_repository.get_by_id(
                    lancamento_data.id_fornecedor, 
                    id_empresa
                )
                if not fornecedor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Fornecedor não encontrado ou não pertence a esta empresa"
                    )
            
            # Verificar se conta bancária existe e pertence à empresa
            conta = await self.conta_repository.get_by_id(
                lancamento_data.id_conta, 
                id_empresa
            )
            if not conta:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conta bancária não encontrada ou não pertence a esta empresa"
                )
            
            # Verificar se forma de pagamento existe e pertence à empresa
            forma = await self.forma_pagamento_repository.get_by_id(
                lancamento_data.id_forma_pagamento, 
                id_empresa
            )
            if not forma:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Forma de pagamento não encontrada ou não pertence a esta empresa"
                )
            
            # Preparar dados para criação
            lancamento_dict = lancamento_data.model_dump()
            
            # Criar o lançamento
            lancamento = await self.repository.create(lancamento_dict)
            
            # Atualizar saldo da conta se o lançamento estiver efetivado
            if lancamento.status == "efetivado":
                await self._atualizar_saldo_conta(lancamento)
            
            return LancamentoSchema.model_validate(lancamento)
            
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro ao criar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar lançamento: {str(e)}"
            )

    async def atualizar_lancamento(
        self, 
        id_lancamento: UUID, 
        lancamento_data: LancamentoUpdate, 
        id_empresa: UUID
    ) -> LancamentoSchema:
        """
        Atualizar lançamento existente.
        
        Args:
            id_lancamento: ID do lançamento
            lancamento_data: Dados para atualização
            id_empresa: ID da empresa
            
        Returns:
            Lançamento atualizado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou houver erro
        """
        logger.info(f"Atualizando lançamento {id_lancamento}")
        
        try:
            # Verificar se o lançamento existe
            lancamento_atual = await self.repository.get_by_id(id_lancamento, id_empresa)
            
            if not lancamento_atual:
                logger.warning(f"Lançamento {id_lancamento} não encontrado para atualização")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
            
            # Guardar status e conta antigos para verificar mudanças
            status_antigo = lancamento_atual.status
            conta_antiga_id = lancamento_atual.id_conta
            
            # Verificar se cliente existe, se estiver sendo alterado
            if lancamento_data.id_cliente and lancamento_data.id_cliente != lancamento_atual.id_cliente:
                cliente = await self.cliente_repository.get_by_id(
                    lancamento_data.id_cliente, 
                    id_empresa
                )
                if not cliente:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente não encontrado ou não pertence a esta empresa"
                    )
            
            # Verificar se fornecedor existe, se estiver sendo alterado
            if lancamento_data.id_fornecedor and lancamento_data.id_fornecedor != lancamento_atual.id_fornecedor:
                fornecedor = await self.fornecedor_repository.get_by_id(
                    lancamento_data.id_fornecedor, 
                    id_empresa
                )
                if not fornecedor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Fornecedor não encontrado ou não pertence a esta empresa"
                    )
            
            # Verificar se conta bancária existe, se estiver sendo alterada
            if lancamento_data.id_conta and lancamento_data.id_conta != lancamento_atual.id_conta:
                conta = await self.conta_repository.get_by_id(
                    lancamento_data.id_conta, 
                    id_empresa
                )
                if not conta:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conta bancária não encontrada ou não pertence a esta empresa"
                    )
            
            # Verificar se forma de pagamento existe, se estiver sendo alterada
            if lancamento_data.id_forma_pagamento and lancamento_data.id_forma_pagamento != lancamento_atual.id_forma_pagamento:
                forma = await self.forma_pagamento_repository.get_by_id(
                    lancamento_data.id_forma_pagamento, 
                    id_empresa
                )
                if not forma:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Forma de pagamento não encontrada ou não pertence a esta empresa"
                    )
            
            # Verificar consistência entre status e data de efetivação
            if lancamento_data.status == "efetivado" and not lancamento_atual.data_efetivacao:
                if not lancamento_data.data_efetivacao:
                    lancamento_data.data_efetivacao = datetime.now()
            
            # Preparar dados para atualização
            lancamento_dict = lancamento_data.model_dump(exclude_unset=True)
            
            # Atualizar lançamento
            lancamento_atualizado = await self.repository.update(
                id_lancamento, 
                id_empresa, 
                lancamento_dict
            )
            
            if not lancamento_atualizado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
            
            # Atualizar saldo da conta se o status mudou para/de efetivado ou se a conta mudou
            if (status_antigo != lancamento_atualizado.status and 
                (status_antigo == "efetivado" or lancamento_atualizado.status == "efetivado")):
                await self._atualizar_saldo_conta(lancamento_atualizado)
                
                # Se mudou de conta, estornar da conta antiga
                if lancamento_atualizado.status == "efetivado" and conta_antiga_id != lancamento_atualizado.id_conta:
                    await self._estornar_saldo_conta(lancamento_atualizado, conta_antiga_id)
            
            return LancamentoSchema.model_validate(lancamento_atualizado)
            
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar lançamento: {str(e)}"
            )

    async def remover_lancamento(self, id_lancamento: UUID, id_empresa: UUID) -> bool:
        """
        Remover lançamento.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa
            
        Returns:
            True se removido com sucesso
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou se houver erro
        """
        logger.info(f"Removendo lançamento {id_lancamento}")
        
        try:
            # Verificar se o lançamento existe
            lancamento = await self.repository.get_by_id(id_lancamento, id_empresa)
            
            if not lancamento:
                logger.warning(f"Lançamento {id_lancamento} não encontrado para remoção")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
            
            # Se o lançamento estiver efetivado, estornar o saldo da conta
            if lancamento.status == "efetivado":
                await self._estornar_saldo_conta(lancamento)
            
            # Remover o lançamento
            sucesso = await self.repository.delete(id_lancamento, id_empresa)
            
            if not sucesso:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado ou não pôde ser removido"
                )
                
            return True
            
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro ao remover lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover lançamento: {str(e)}"
            )

    async def efetivar_lancamento(self, id_lancamento: UUID, id_empresa: UUID, data_efetivacao: Optional[date] = None) -> LancamentoSchema:
        """
        Efetivar um lançamento (alterar status de pendente para efetivado).
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa
            data_efetivacao: Data de efetivação (opcional, padrão=hoje)
            
        Returns:
            Lançamento efetivado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou houver erro
        """
        logger.info(f"Efetivando lançamento {id_lancamento}")
        
        try:
            # Buscar o lançamento
            lancamento = await self.repository.get_by_id(id_lancamento, id_empresa)
            
            if not lancamento:
                logger.warning(f"Lançamento {id_lancamento} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
            
            # Verificar se já está efetivado
            if lancamento.status == "efetivado":
                return LancamentoSchema.model_validate(lancamento)
            
            # Verificar se está cancelado
            if lancamento.status == "cancelado":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não é possível efetivar um lançamento cancelado"
                )
            
            # Efetivar o lançamento
            lancamento_efetivado = await self.repository.efetivar_lancamento(id_lancamento, id_empresa)
            
            # Atualizar saldo da conta
            await self._atualizar_saldo_conta(lancamento_efetivado)
            
            return LancamentoSchema.model_validate(lancamento_efetivado)
            
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro ao efetivar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao efetivar lançamento: {str(e)}"
            )

    async def cancelar_lancamento(self, id_lancamento: UUID, id_empresa: UUID) -> LancamentoSchema:
        """
        Cancelar um lançamento.
        
        Args:
            id_lancamento: ID do lançamento
            id_empresa: ID da empresa
            
        Returns:
            Lançamento cancelado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou houver erro
        """
        logger.info(f"Cancelando lançamento {id_lancamento}")
        
        try:
            # Buscar o lançamento
            lancamento = await self.repository.get_by_id(id_lancamento, id_empresa)
            
            if not lancamento:
                logger.warning(f"Lançamento {id_lancamento} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
            
            # Verificar se já está cancelado
            if lancamento.status == "cancelado":
                return LancamentoSchema.model_validate(lancamento)
            
            # Se estava efetivado, estornar o saldo da conta
            if lancamento.status == "efetivado":
                await self._estornar_saldo_conta(lancamento)
            
            # Cancelar o lançamento
            lancamento_cancelado = await self.repository.cancelar_lancamento(id_lancamento, id_empresa)
            
            return LancamentoSchema.model_validate(lancamento_cancelado)
            
        except HTTPException:
            # Repassar exceções HTTP
            raise
        except Exception as e:
            logger.error(f"Erro ao cancelar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao cancelar lançamento: {str(e)}"
            )

    async def get_totais(
        self, 
        id_empresa: UUID,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        id_cliente: Optional[UUID] = None,
        id_fornecedor: Optional[UUID] = None,
        id_conta: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Calcular totais de lançamentos.
        
        Args:
            id_empresa: ID da empresa
            data_inicio: Filtrar por data inicial
            data_fim: Filtrar por data final
            id_cliente: Filtrar por cliente
            id_fornecedor: Filtrar por fornecedor
            id_conta: Filtrar por conta bancária
            
        Returns:
            Dicionário com os totais calculados
        """
        logger.info(f"Calculando totais de lançamentos para empresa {id_empresa}")
        
        try:
            # Obter lançamentos de receita
            receitas, _ = await self.repository.get_by_empresa(
                id_empresa=id_empresa,
                tipo="receita",
                data_inicio=data_inicio,
                data_fim=data_fim,
                id_cliente=id_cliente,
                id_fornecedor=id_fornecedor,
                id_conta=id_conta,
                status="efetivado"
            )
            
            # Obter lançamentos de despesa
            despesas, _ = await self.repository.get_by_empresa(
                id_empresa=id_empresa,
                tipo="despesa",
                data_inicio=data_inicio,
                data_fim=data_fim,
                id_cliente=id_cliente,
                id_fornecedor=id_fornecedor,
                id_conta=id_conta,
                status="efetivado"
            )
            
            # Obter lançamentos pendentes
            pendentes, _ = await self.repository.get_by_empresa(
                id_empresa=id_empresa,
                data_inicio=data_inicio,
                data_fim=data_fim,
                id_cliente=id_cliente,
                id_fornecedor=id_fornecedor,
                id_conta=id_conta,
                status="pendente"
            )
            
            # Obter lançamentos cancelados
            cancelados, _ = await self.repository.get_by_empresa(
                id_empresa=id_empresa,
                data_inicio=data_inicio,
                data_fim=data_fim,
                id_cliente=id_cliente,
                id_fornecedor=id_fornecedor,
                id_conta=id_conta,
                status="cancelado"
            )
            
            # Calcular totais
            total_receitas = sum(l.valor for l in receitas)
            total_despesas = sum(l.valor for l in despesas)
            total_pendentes = sum(l.valor for l in pendentes)
            total_cancelados = sum(l.valor for l in cancelados)
            saldo = total_receitas - total_despesas
            
            return {
                "total_receitas": float(total_receitas),
                "total_despesas": float(total_despesas),
                "saldo": float(saldo),
                "total_pendentes": float(total_pendentes),
                "total_efetivados": float(total_receitas + total_despesas),
                "total_cancelados": float(total_cancelados)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular totais de lançamentos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao calcular totais de lançamentos: {str(e)}"
            )

    async def _atualizar_saldo_conta(
        self, 
        lancamento: Lancamento
    ) -> None:
        """
        Atualizar o saldo da conta bancária com base no lançamento.
        
        Args:
            lancamento: Objeto do lançamento
        """
        try:
            # Se foi cancelado, não alterar o saldo
            if lancamento.status == "cancelado":
                return
            
            # Buscar a conta
            conta = await self.conta_repository.get_by_id(lancamento.id_conta, lancamento.id_empresa)
            if not conta:
                logger.warning(f"Conta bancária não encontrada para atualização de saldo: {lancamento.id_conta}")
                return
            
            # Se for efetivado e receita, aumentar o saldo
            if lancamento.status == "efetivado" and lancamento.tipo == "receita":
                conta.saldo_atual += lancamento.valor
            
            # Se for efetivado e despesa, diminuir o saldo
            if lancamento.status == "efetivado" and lancamento.tipo == "despesa":
                conta.saldo_atual -= lancamento.valor
            
            # Atualizar a conta
            await self.conta_repository.update(conta.id_conta, {"saldo_atual": conta.saldo_atual}, lancamento.id_empresa)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar saldo da conta: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar saldo da conta: {str(e)}"
            )

    async def _estornar_saldo_conta(
        self, 
        lancamento: Lancamento, 
        id_conta_antiga: Optional[UUID] = None
    ) -> None:
        """
        Estornar o valor do lançamento do saldo da conta.
        
        Args:
            lancamento: Objeto do lançamento
            id_conta_antiga: ID da conta anterior, se houve mudança de conta
        """
        try:
            # Determinar qual conta usar
            id_conta = id_conta_antiga if id_conta_antiga else lancamento.id_conta
            
            # Buscar a conta
            conta = await self.conta_repository.get_by_id(id_conta, lancamento.id_empresa)
            if not conta:
                logger.warning(f"Conta bancária não encontrada para estorno: {id_conta}")
                return
            
            # Estornar conforme o tipo
            if lancamento.tipo == "receita":
                conta.saldo_atual -= lancamento.valor
            else:
                conta.saldo_atual += lancamento.valor
            
            # Atualizar a conta
            await self.conta_repository.update(conta.id_conta, {"saldo_atual": conta.saldo_atual}, lancamento.id_empresa)
            
        except Exception as e:
            logger.error(f"Erro ao estornar saldo da conta: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao estornar saldo da conta: {str(e)}"
            )
