"""Repositório para operações de banco de dados relacionadas a centros de custo."""
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.centro_custo import CentroCusto
from app.repositories.base_repository import BaseRepository


class CentroCustoRepository:
    """Repositório para operações com centros de custo."""

    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão do banco de dados."""
        self.session = session

    async def get_by_id(self, id_centro_custo: UUID, id_empresa: Optional[UUID] = None) -> Optional[CentroCusto]:
        """
        Buscar centro de custo pelo ID.
        
        Args:
            id_centro_custo: ID do centro de custo
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            CentroCusto se encontrado, None caso contrário
        """
        query = select(CentroCusto).where(CentroCusto.id_centro_custo == id_centro_custo)
        
        if id_empresa:
            query = query.where(CentroCusto.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_descricao(self, descricao: str, id_empresa: UUID) -> Optional[CentroCusto]:
        """
        Buscar centro de custo pela descrição e empresa.
        
        Args:
            descricao: Descrição do centro de custo
            id_empresa: ID da empresa
            
        Returns:
            CentroCusto se encontrado, None caso contrário
        """
        query = select(CentroCusto).where(
            CentroCusto.descricao == descricao,
            CentroCusto.id_empresa == id_empresa
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_empresa(
        self, 
        id_empresa: UUID, 
        skip: int = 0, 
        limit: int = 100,
        descricao: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Tuple[List[CentroCusto], int]:
        """
        Listar centros de custo de uma empresa com paginação e filtros opcionais.
        
        Args:
            id_empresa: ID da empresa para filtrar
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            descricao: Filtrar por descrição (opcional)
            ativo: Filtrar por status (opcional)
            
        Returns:
            Tupla contendo lista de centros de custo e contagem total
        """
        filters = [CentroCusto.id_empresa == id_empresa]
        
        if descricao:
            filters.append(CentroCusto.descricao.ilike(f"%{descricao}%"))
            
        if ativo is not None:
            filters.append(CentroCusto.ativo == ativo)
            
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters
        )

    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[List] = None
    ) -> Tuple[List[CentroCusto], int]:
        """
        Buscar múltiplos centros de custo com paginação e filtros.
        
        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            filters: Filtros adicionais (opcional)
            
        Returns:
            Tupla contendo lista de centros de custo e contagem total
        """
        filters = filters or []
        
        # Consulta para obter os dados
        query = select(CentroCusto).where(*filters).offset(skip).limit(limit)
        results = await self.session.execute(query)
        items = results.scalars().all()
        
        # Consulta para obter contagem total
        count_query = select(func.count()).select_from(CentroCusto).where(*filters)
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar_one()
        
        return list(items), total_count
    
    async def get_count(self, filters: Optional[List] = None) -> int:
        """
        Obter contagem de centros de custo com filtros opcionais.
        
        Args:
            filters: Filtros para a contagem (opcional)
            
        Returns:
            Número total de centros de custo que correspondem aos filtros
        """
        filters = filters or []
        
        query = select(func.count()).select_from(CentroCusto).where(*filters)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def create(self, data: Dict[str, Any]) -> CentroCusto:
        """
        Criar novo centro de custo com validação de duplicidade.
        
        Args:
            data: Dados do centro de custo a ser criado
            
        Returns:
            Novo centro de custo criado
        """
        try:
            # Verificar duplicação de descrição na mesma empresa
            existente = await self.get_by_descricao(
                descricao=data['descricao'],
                id_empresa=data['id_empresa']
            )
            
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um centro de custo com descrição '{data['descricao']}' nesta empresa"
                )
                
            centro_custo = CentroCusto(**data)
            self.session.add(centro_custo)
            await self.session.commit()
            await self.session.refresh(centro_custo)
            return centro_custo
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar centro de custo: {str(e)}"
            )

    async def update(self, id_centro_custo: UUID, data: Dict[str, Any], id_empresa: Optional[UUID] = None) -> Optional[CentroCusto]:
        """
        Atualizar centro de custo existente com validação de empresa.
        
        Args:
            id_centro_custo: ID do centro de custo
            data: Dados para atualização
            id_empresa: ID da empresa para verificação (opcional)
            
        Returns:
            CentroCusto atualizado ou None se não encontrado
        """
        try:
            # Verificar se o centro de custo existe
            centro_custo = await self.get_by_id(id_centro_custo, id_empresa)
            if not centro_custo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Centro de custo não encontrado"
                )
                
            if 'descricao' in data:
                # Verificar duplicação de descrição na mesma empresa
                existente = await self.get_by_descricao(
                    descricao=data['descricao'],
                    id_empresa=id_empresa or centro_custo.id_empresa
                )
                
                if existente and existente.id_centro_custo != id_centro_custo:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Já existe um centro de custo com descrição '{data['descricao']}' nesta empresa"
                    )
            
            # Atualizar atributos
            for key, value in data.items():
                if hasattr(centro_custo, key):
                    setattr(centro_custo, key, value)
            
            await self.session.commit()
            await self.session.refresh(centro_custo)
            return centro_custo
        except HTTPException:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar centro de custo: {str(e)}"
            )

    async def delete(self, id_centro_custo: UUID, id_empresa: Optional[UUID] = None) -> bool:
        """
        Excluir centro de custo com validação de empresa.
        
        Args:
            id_centro_custo: ID do centro de custo a ser excluído
            id_empresa: ID da empresa para verificação (opcional)
            
        Returns:
            True se excluído com sucesso
        """
        try:
            # Verificar se o centro de custo existe
            centro_custo = await self.get_by_id(id_centro_custo, id_empresa)
            if not centro_custo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Centro de custo não encontrado"
                )
                
            await self.session.delete(centro_custo)
            await self.session.commit()
            return True
        except HTTPException:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir centro de custo: {str(e)}"
            )

    async def toggle_ativo(self, id_centro_custo: UUID, id_empresa: Optional[UUID] = None) -> CentroCusto:
        """
        Alternar o status ativo/inativo de um centro de custo.
        
        Args:
            id_centro_custo: ID do centro de custo
            id_empresa: ID da empresa para verificação (opcional)
            
        Returns:
            Centro de custo atualizado
        """
        try:
            # Verificar se o centro de custo existe
            centro_custo = await self.get_by_id(id_centro_custo, id_empresa)
            if not centro_custo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Centro de custo não encontrado"
                )
                
            # Inverter o status
            centro_custo.ativo = not centro_custo.ativo
            
            await self.session.commit()
            await self.session.refresh(centro_custo)
            return centro_custo
        except HTTPException:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao alternar status do centro de custo: {str(e)}"
            ) 