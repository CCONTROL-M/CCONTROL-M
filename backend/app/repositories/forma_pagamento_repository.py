"""Repositório para operações com formas de pagamento."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from fastapi import HTTPException, status

from app.models.forma_pagamento import FormaPagamento
from app.models.lancamento import Lancamento
from app.schemas.forma_pagamento import FormaPagamentoCreate, FormaPagamentoUpdate
from app.repositories.base_repository import BaseRepository


class FormaPagamentoRepository(BaseRepository[FormaPagamento, FormaPagamentoCreate, FormaPagamentoUpdate]):
    """Repositório para operações com formas de pagamento."""
    
    def __init__(self, session: AsyncSession):
        """Inicializa o repositório com o modelo FormaPagamento."""
        self.session = session
        super().__init__(FormaPagamento)
    
    async def get_by_id(self, id_forma: UUID, id_empresa: UUID = None) -> Optional[FormaPagamento]:
        """
        Buscar forma de pagamento pelo ID e empresa.
        
        Args:
            id_forma: ID da forma de pagamento
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            FormaPagamento se encontrada, None caso contrário
        """
        query = select(FormaPagamento).where(FormaPagamento.id_forma == id_forma)
        
        if id_empresa:
            query = query.where(FormaPagamento.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_entity_id(self, id: UUID) -> Optional[FormaPagamento]:
        """
        Obtém uma forma de pagamento pelo ID.
        
        Args:
            id: ID da forma de pagamento
            
        Returns:
            FormaPagamento: Forma de pagamento encontrada ou None
        """
        query = select(FormaPagamento).where(FormaPagamento.id_forma == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_nome(
        self, 
        nome: str,
        id_empresa: UUID
    ) -> Optional[FormaPagamento]:
        """
        Obtém uma forma de pagamento pelo nome.
        
        Args:
            nome: Nome da forma de pagamento
            id_empresa: ID da empresa
            
        Returns:
            FormaPagamento: Forma de pagamento encontrada ou None
        """
        query = select(FormaPagamento).where(
            FormaPagamento.nome == nome,
            FormaPagamento.id_empresa == id_empresa
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_empresa(
        self, 
        id_empresa: UUID,
        ativa: Optional[bool] = None
    ) -> List[FormaPagamento]:
        """
        Obtém todas as formas de pagamento de uma empresa.
        
        Args:
            id_empresa: ID da empresa
            ativa: Filtrar por status de ativação
            
        Returns:
            List[FormaPagamento]: Lista de formas de pagamento da empresa
        """
        query = select(FormaPagamento).where(FormaPagamento.id_empresa == id_empresa)
        
        if ativa is not None:
            query = query.where(FormaPagamento.ativa == ativa)
            
        query = query.order_by(FormaPagamento.nome)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        ativa: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[FormaPagamento]:
        """
        Obtém múltiplas formas de pagamento com paginação e filtragem opcional.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            ativa: Filtrar por status de ativação
            filters: Filtros adicionais
            
        Returns:
            List[FormaPagamento]: Lista de formas de pagamento
        """
        query = select(FormaPagamento)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.where(FormaPagamento.id_empresa == id_empresa)
            
        if ativa is not None:
            query = query.where(FormaPagamento.ativa == ativa)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(FormaPagamento.nome.ilike(termo_busca))
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(FormaPagamento, field) and field not in ["nome"]:
                    query = query.where(getattr(FormaPagamento, field) == value)
        
        # Ordenação padrão por nome
        query = query.order_by(FormaPagamento.nome)
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_count(
        self, 
        id_empresa: Optional[UUID] = None,
        ativa: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de formas de pagamento com filtros opcionais.
        
        Args:
            id_empresa: Filtrar por empresa específica
            ativa: Filtrar por status de ativação
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de formas de pagamento
        """
        query = select(func.count()).select_from(FormaPagamento)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.where(FormaPagamento.id_empresa == id_empresa)
            
        if ativa is not None:
            query = query.where(FormaPagamento.ativa == ativa)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(FormaPagamento.nome.ilike(termo_busca))
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(FormaPagamento, field) and field not in ["nome"]:
                    query = query.where(getattr(FormaPagamento, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one() or 0
    
    async def create(self, data: Dict[str, Any]) -> FormaPagamento:
        """
        Cria uma nova forma de pagamento.
        
        Args:
            data: Dados da forma de pagamento
            
        Returns:
            FormaPagamento: Forma de pagamento criada
            
        Raises:
            HTTPException: Se já existir uma forma de pagamento com o mesmo nome
        """
        try:
            # Verificar se já existe forma de pagamento com o mesmo nome
            forma_existente = await self.get_by_nome(data["nome"], data["id_empresa"])
            if forma_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma forma de pagamento com este nome para esta empresa"
                )
            
            # Criar objeto forma de pagamento
            db_obj = FormaPagamento(**data)
            
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return db_obj
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar forma de pagamento: {str(e)}"
            )
    
    async def update(self, id_forma: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[FormaPagamento]:
        """
        Atualiza uma forma de pagamento existente.
        
        Args:
            id_forma: ID da forma de pagamento
            data: Dados para atualização
            id_empresa: ID da empresa para validação
            
        Returns:
            FormaPagamento: Forma de pagamento atualizada ou None se não encontrada
            
        Raises:
            HTTPException: Se o novo nome já estiver em uso
        """
        try:
            # Primeiro verificar se a forma de pagamento existe e pertence à empresa
            forma = await self.get_by_id(id_forma, id_empresa)
            if not forma:
                return None
            
            data_copy = data.copy()
            
            # Verificar se está alterando o nome e se o novo nome já existe
            if "nome" in data_copy and data_copy["nome"] != forma.nome:
                forma_existente = await self.get_by_nome(data_copy["nome"], id_empresa)
                if forma_existente and forma_existente.id_forma != id_forma:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Já existe uma forma de pagamento com este nome para esta empresa"
                    )
            
            # Atualizar campos
            for field, value in data_copy.items():
                if hasattr(forma, field):
                    setattr(forma, field, value)
            
            self.session.add(forma)
            await self.session.commit()
            await self.session.refresh(forma)
            
            return forma
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar forma de pagamento: {str(e)}"
            )
    
    async def delete(self, id_forma: UUID, id_empresa: UUID) -> bool:
        """
        Exclui uma forma de pagamento.
        
        Args:
            id_forma: ID da forma de pagamento
            id_empresa: ID da empresa para validação
            
        Returns:
            bool: True se removida com sucesso
            
        Raises:
            HTTPException: Se a forma de pagamento não existe ou já está em uso
        """
        try:
            # Verificar se a forma existe e pertence à empresa
            forma = await self.get_by_id(id_forma, id_empresa)
            if not forma:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Forma de pagamento não encontrada"
                )
            
            # Verificar se existem lançamentos usando esta forma de pagamento
            query = select(Lancamento).where(Lancamento.id_forma_pagamento == id_forma).limit(1)
            result = await self.session.execute(query)
            lancamento = result.scalar_one_or_none()
            
            if lancamento:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Não é possível excluir uma forma de pagamento que está sendo utilizada em lançamentos"
                )
            
            # Remover forma de pagamento
            await self.session.delete(forma)
            await self.session.commit()
            
            return True
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir forma de pagamento: {str(e)}"
            )
    
    async def toggle_ativa(self, id_forma: UUID, id_empresa: UUID) -> FormaPagamento:
        """
        Alterna o status de ativação da forma de pagamento.
        
        Args:
            id_forma: ID da forma de pagamento
            id_empresa: ID da empresa para validação
            
        Returns:
            FormaPagamento: Forma de pagamento com status alterado
            
        Raises:
            HTTPException: Se a forma de pagamento não existe
        """
        try:
            # Verificar se a forma existe e pertence à empresa
            forma = await self.get_by_id(id_forma, id_empresa)
            if not forma:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Forma de pagamento não encontrada"
                )
            
            # Alternar status
            forma.ativa = not forma.ativa
            
            self.session.add(forma)
            await self.session.commit()
            await self.session.refresh(forma)
            
            return forma
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao alternar status da forma de pagamento: {str(e)}"
            ) 