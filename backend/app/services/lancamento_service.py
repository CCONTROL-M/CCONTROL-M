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
from app.services.auditoria_service import AuditoriaService


# Configurar logger
logger = logging.getLogger(__name__)


class LancamentoService:
    """Serviço para gerenciamento de lançamentos."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = LancamentoRepository(session)
        self.cliente_repository = ClienteRepository(session)
        self.fornecedor_repository = FornecedorRepository(session)
        self.conta_bancaria_repository = ContaBancariaRepository(session)
        self.forma_pagamento_repository = FormaPagamentoRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logger

    async def create(
        self,
        lancamento: LancamentoCreate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> LancamentoSchema:
        """
        Criar um novo lançamento.
        
        Args:
            lancamento: Dados do lançamento a ser criado
            usuario_id: ID do usuário que está criando o lançamento
            empresa_id: ID da empresa
            
        Returns:
            Lançamento criado
            
        Raises:
            HTTPException: Se houver erro na criação
        """
        try:
            # Validar cliente/fornecedor
            if lancamento.id_cliente:
                cliente = await self.cliente_repository.get_by_id(lancamento.id_cliente)
                if not cliente:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente não encontrado"
                    )
            elif lancamento.id_fornecedor:
                fornecedor = await self.fornecedor_repository.get_by_id(lancamento.id_fornecedor)
                if not fornecedor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Fornecedor não encontrado"
                    )
            
            # Criar lançamento
            novo_lancamento = await self.repository.create(lancamento, empresa_id)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CRIAR_LANCAMENTO",
                detalhes={
                    "id_lancamento": str(novo_lancamento.id_lancamento),
                    "valor": float(novo_lancamento.valor),
                    "data": novo_lancamento.data.isoformat(),
                    "tipo": novo_lancamento.tipo,
                    "status": novo_lancamento.status
                },
                empresa_id=empresa_id
            )
            
            return novo_lancamento
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao criar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar lançamento"
            )

    async def update(
        self,
        id_lancamento: UUID,
        lancamento: LancamentoUpdate,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> LancamentoSchema:
        """
        Atualizar um lançamento existente.
        
        Args:
            id_lancamento: ID do lançamento a ser atualizado
            lancamento: Dados atualizados do lançamento
            usuario_id: ID do usuário que está atualizando o lançamento
            empresa_id: ID da empresa
            
        Returns:
            Lançamento atualizado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou houver erro na atualização
        """
        try:
            # Obter lançamento atual
            lancamento_atual = await self.repository.get_by_id(id_lancamento, empresa_id)
            if not lancamento_atual:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
            
            # Atualizar lançamento
            lancamento_atualizado = await self.repository.update(
                id_lancamento, lancamento, empresa_id
            )
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_LANCAMENTO",
                detalhes={
                    "id_lancamento": str(id_lancamento),
                    "valor_anterior": float(lancamento_atual.valor),
                    "valor_atual": float(lancamento_atualizado.valor),
                    "descricao": lancamento_atualizado.descricao,
                    "status_anterior": lancamento_atual.status,
                    "status_atual": lancamento_atualizado.status
                },
                empresa_id=empresa_id
            )
            
            return lancamento_atualizado
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao atualizar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar lançamento"
            )

    async def delete(
        self,
        id_lancamento: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> Dict[str, str]:
        """
        Excluir um lançamento.
        
        Args:
            id_lancamento: ID do lançamento a ser excluído
            usuario_id: ID do usuário que está excluindo o lançamento
            empresa_id: ID da empresa
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou houver erro na exclusão
        """
        try:
            # Obter lançamento para registrar log
            lancamento = await self.repository.get_by_id(id_lancamento, empresa_id)
            if not lancamento:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
            
            # Excluir lançamento
            await self.repository.delete(id_lancamento, empresa_id)
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="EXCLUIR_LANCAMENTO",
                detalhes={
                    "id_lancamento": str(id_lancamento),
                    "valor": float(lancamento.valor),
                    "descricao": lancamento.descricao,
                    "data": lancamento.data.isoformat(),
                    "tipo": lancamento.tipo,
                    "status": lancamento.status
                },
                empresa_id=empresa_id
            )
            
            return {"message": "Lançamento excluído com sucesso"}
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao excluir lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao excluir lançamento"
            )

    async def get_by_id(
        self,
        id_lancamento: UUID,
        usuario_id: UUID,
        empresa_id: UUID
    ) -> LancamentoSchema:
        """
        Buscar um lançamento pelo ID.
        
        Args:
            id_lancamento: ID do lançamento a ser buscado
            usuario_id: ID do usuário que está buscando
            empresa_id: ID da empresa
            
        Returns:
            Lançamento encontrado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado
        """
        try:
            lancamento = await self.repository.get_by_id(id_lancamento)
            if not lancamento:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
                
            # Registrar ação de consulta
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="CONSULTAR_LANCAMENTO",
                detalhes={"id_lancamento": str(id_lancamento)},
                empresa_id=empresa_id
            )
                
            return lancamento
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao buscar lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar lançamento"
            )

    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        id_cliente: Optional[UUID] = None,
        id_fornecedor: Optional[UUID] = None,
        status: Optional[str] = None,
        tipo: Optional[str] = None,
        data_inicial: Optional[date] = None,
        data_final: Optional[date] = None,
        busca: Optional[str] = None
    ) -> PaginatedResponse[LancamentoSchema]:
        """
        Buscar múltiplos lançamentos com filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            id_cliente: Filtrar por cliente
            id_fornecedor: Filtrar por fornecedor
            status: Filtrar por status
            tipo: Filtrar por tipo
            data_inicial: Data inicial para filtro
            data_final: Data final para filtro
            busca: Termo para busca
            
        Returns:
            Lista paginada de lançamentos
        """
        try:
            lancamentos, total = await self.repository.get_multi(
                empresa_id=empresa_id,
                skip=skip,
                limit=limit,
                id_cliente=id_cliente,
                id_fornecedor=id_fornecedor,
                status=status,
                tipo=tipo,
                data_inicial=data_inicial,
                data_final=data_final,
                busca=busca
            )
            
            return PaginatedResponse(
                items=lancamentos,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 1
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar lançamentos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar lançamentos"
            )

    async def atualizar_status(
        self,
        id_lancamento: UUID,
        status: StatusLancamento,
        usuario_id: UUID,
        empresa_id: UUID,
        observacao: Optional[str] = None
    ) -> LancamentoSchema:
        """
        Atualizar o status de um lançamento.
        
        Args:
            id_lancamento: ID do lançamento
            status: Novo status
            usuario_id: ID do usuário que está atualizando
            empresa_id: ID da empresa
            observacao: Observação opcional sobre a mudança de status
            
        Returns:
            Lançamento atualizado
            
        Raises:
            HTTPException: Se o lançamento não for encontrado ou houver erro na atualização
        """
        try:
            # Obter lançamento atual
            lancamento_atual = await self.repository.get_by_id(id_lancamento, empresa_id)
            if not lancamento_atual:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lançamento não encontrado"
                )
            
            # Verificar se o status é igual ao atual
            if lancamento_atual.status == status:
                return lancamento_atual
            
            # Atualizar status
            lancamento_atualizado = await self.repository.update_status(
                id_lancamento, status, empresa_id, observacao
            )
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=usuario_id,
                acao="ATUALIZAR_STATUS_LANCAMENTO",
                detalhes={
                    "id_lancamento": str(id_lancamento),
                    "status_anterior": lancamento_atual.status,
                    "status_novo": status,
                    "observacao": observacao
                },
                empresa_id=empresa_id
            )
            
            return lancamento_atualizado
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status do lançamento: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar status do lançamento"
            )

    async def listar_lancamentos(
        self,
        id_empresa: UUID,
        tipo: Optional[str] = None,
        id_categoria: Optional[UUID] = None,
        id_centro_custo: Optional[UUID] = None,
        id_conta: Optional[UUID] = None,
        status: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[LancamentoSchema], int]:
        """
        Listar lançamentos com filtros.
        
        Args:
            id_empresa: ID da empresa
            tipo: Tipo do lançamento (receita/despesa)
            id_categoria: ID da categoria
            id_centro_custo: ID do centro de custo
            id_conta: ID da conta bancária
            status: Status do lançamento
            data_inicio: Data inicial (formato YYYY-MM-DD)
            data_fim: Data final (formato YYYY-MM-DD)
            page: Número da página
            page_size: Tamanho da página
            
        Returns:
            Tupla com lista de lançamentos e contagem total
        """
        try:
            # Converter datas se fornecidas
            data_inicio_obj = None
            data_fim_obj = None
            
            if data_inicio:
                try:
                    data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d").date()
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Formato de data_inicio inválido. Use YYYY-MM-DD."
                    )
            
            if data_fim:
                try:
                    data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d").date()
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Formato de data_fim inválido. Use YYYY-MM-DD."
                    )
            
            # Calcular skip para paginação
            skip = (page - 1) * page_size
            
            # Chamar o repositório para obter os dados
            lancamentos, total = await self.repository.get_by_empresa(
                id_empresa=id_empresa,
                skip=skip,
                limit=page_size,
                tipo=tipo,
                data_inicio=data_inicio_obj,
                data_fim=data_fim_obj,
                id_cliente=None,  # Não implementado no filtro
                id_fornecedor=None,  # Não implementado no filtro
                id_conta=id_conta,
                status=status
            )
            
            # Converter para schema e retornar
            lancamentos_schema = [LancamentoSchema.model_validate(lancamento) for lancamento in lancamentos]
            return lancamentos_schema, total
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Erro ao listar lançamentos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao listar lançamentos"
            )
