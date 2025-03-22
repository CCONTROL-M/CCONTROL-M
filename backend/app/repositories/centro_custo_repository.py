"""Repositório para operações de banco de dados relacionadas a centros de custo."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.centro_custo import CentroCusto
from app.repositories.base_repository import BaseRepository


class CentroCustoRepository(BaseRepository):
    """Repositório para operações com centros de custo."""

    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão e modelo."""
        super().__init__(session, CentroCusto)

    async def get_by_nome_empresa(self, nome: str, id_empresa: UUID) -> Optional[CentroCusto]:
        """
        Buscar centro de custo pelo nome e empresa.
        
        Args:
            nome: Nome do centro de custo
            id_empresa: ID da empresa
            
        Returns:
            CentroCusto se encontrado, None caso contrário
        """
        query = select(CentroCusto).where(
            CentroCusto.nome == nome,
            CentroCusto.id_empresa == id_empresa
        )
        
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_with_filters(
        self, 
        skip: int = 0, 
        limit: int = 100,
        id_empresa: UUID = None,
        nome: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> tuple[List[CentroCusto], int]:
        """
        Listar centros de custo com filtros e paginação.
        
        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            id_empresa: ID da empresa para filtrar
            nome: Filtrar por nome
            ativo: Filtrar por status
            
        Returns:
            Lista de centros de custo e contagem total
        """
        filters = []
        
        if id_empresa:
            filters.append(CentroCusto.id_empresa == id_empresa)
        
        if nome:
            filters.append(CentroCusto.nome.ilike(f"%{nome}%"))
            
        if ativo is not None:
            filters.append(CentroCusto.ativo == ativo)
            
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def update_centro_custo(self, id_centro: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[CentroCusto]:
        """
        Atualizar centro de custo existente com validação de empresa.
        
        Args:
            id_centro: ID do centro de custo
            data: Dados para atualização
            id_empresa: ID da empresa para verificação
            
        Returns:
            CentroCusto atualizado ou None se não encontrado
        """
        if 'nome' in data:
            # Verificar duplicação de nome na mesma empresa
            existente = await self.get_by_nome_empresa(
                nome=data['nome'],
                id_empresa=id_empresa
            )
            
            if existente and existente.id_centro != id_centro:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um centro de custo com nome '{data['nome']}' nesta empresa"
                )
                
        return await self.update(id_centro, data, id_empresa)
        
    async def create_centro_custo(self, data: Dict[str, Any]) -> CentroCusto:
        """
        Criar novo centro de custo com validação de duplicidade.
        
        Args:
            data: Dados do centro de custo a ser criado
            
        Returns:
            Novo centro de custo criado
        """
        # Verificar duplicação de nome na mesma empresa
        existente = await self.get_by_nome_empresa(
            nome=data['nome'],
            id_empresa=data['id_empresa']
        )
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um centro de custo com nome '{data['nome']}' nesta empresa"
            )
            
        return await self.create(data) 