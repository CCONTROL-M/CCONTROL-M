"""Repositório para operações de banco de dados relacionadas a categorias."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.categoria import Categoria
from app.repositories.base_repository import BaseRepository


class CategoriaRepository(BaseRepository):
    """Repositório para operações com categorias."""

    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão e modelo."""
        super().__init__(session, Categoria)

    async def get_by_descricao_empresa(self, descricao: str, id_empresa: UUID) -> Optional[Categoria]:
        """
        Buscar categoria pela descrição e empresa.
        
        Args:
            descricao: Descrição da categoria
            id_empresa: ID da empresa
            
        Returns:
            Categoria se encontrada, None caso contrário
        """
        query = select(Categoria).where(
            Categoria.descricao == descricao,
            Categoria.id_empresa == id_empresa
        )
        
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_with_filters(
        self, 
        skip: int = 0, 
        limit: int = 100,
        id_empresa: UUID = None,
        descricao: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> tuple[List[Categoria], int]:
        """
        Listar categorias com filtros e paginação.
        
        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            id_empresa: ID da empresa para filtrar
            descricao: Filtrar por descrição
            ativo: Filtrar por status
            
        Returns:
            Lista de categorias e contagem total
        """
        filters = []
        
        if id_empresa:
            filters.append(Categoria.id_empresa == id_empresa)
        
        if descricao:
            filters.append(Categoria.descricao.ilike(f"%{descricao}%"))
            
        if ativo is not None:
            filters.append(Categoria.ativo == ativo)
            
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def update_categoria(self, id_categoria: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[Categoria]:
        """
        Atualizar categoria existente com validação de empresa.
        
        Args:
            id_categoria: ID da categoria
            data: Dados para atualização
            id_empresa: ID da empresa para verificação
            
        Returns:
            Categoria atualizada ou None se não encontrada
        """
        if 'descricao' in data:
            # Verificar duplicação de descrição na mesma empresa
            existente = await self.get_by_descricao_empresa(
                descricao=data['descricao'],
                id_empresa=id_empresa
            )
            
            if existente and existente.id_categoria != id_categoria:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe uma categoria com descrição '{data['descricao']}' nesta empresa"
                )
                
        return await self.update(id_categoria, data, id_empresa)
        
    async def create_categoria(self, data: Dict[str, Any]) -> Categoria:
        """
        Criar nova categoria com validação de duplicidade.
        
        Args:
            data: Dados da categoria a ser criada
            
        Returns:
            Nova categoria criada
        """
        # Verificar duplicação de descrição na mesma empresa
        existente = await self.get_by_descricao_empresa(
            descricao=data['descricao'],
            id_empresa=data['id_empresa']
        )
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma categoria com descrição '{data['descricao']}' nesta empresa"
            )
            
        return await self.create(data) 