"""Repositório para operações de banco de dados relacionadas a fornecedores."""
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.fornecedor import Fornecedor
from app.repositories.base_repository import BaseRepository


class FornecedorRepository(BaseRepository):
    """Repositório para operações com fornecedores."""

    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão e modelo."""
        super().__init__(session, Fornecedor)

    async def get_by_cnpj_empresa(self, cnpj: str, id_empresa: UUID) -> Optional[Fornecedor]:
        """
        Buscar fornecedor pelo CNPJ e empresa.
        
        Args:
            cnpj: CNPJ do fornecedor
            id_empresa: ID da empresa
            
        Returns:
            Fornecedor se encontrado, None caso contrário
        """
        query = select(Fornecedor).where(
            Fornecedor.cnpj == cnpj,
            Fornecedor.id_empresa == id_empresa
        )
        
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_with_filters(
        self, 
        skip: int = 0, 
        limit: int = 100,
        id_empresa: UUID = None,
        nome: Optional[str] = None,
        cnpj: Optional[str] = None,
        ativo: Optional[bool] = None,
        avaliacao: Optional[int] = None
    ) -> tuple[List[Fornecedor], int]:
        """
        Listar fornecedores com filtros e paginação.
        
        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            id_empresa: ID da empresa para filtrar
            nome: Filtrar por nome
            cnpj: Filtrar por CNPJ
            ativo: Filtrar por status
            avaliacao: Filtrar por avaliação
            
        Returns:
            Lista de fornecedores e contagem total
        """
        filters = []
        
        if id_empresa:
            filters.append(Fornecedor.id_empresa == id_empresa)
        
        if nome:
            filters.append(Fornecedor.nome.ilike(f"%{nome}%"))
            
        if cnpj:
            filters.append(Fornecedor.cnpj.ilike(f"%{cnpj}%"))
            
        if ativo is not None:
            filters.append(Fornecedor.ativo == ativo)
            
        if avaliacao is not None:
            filters.append(Fornecedor.avaliacao == avaliacao)
            
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def update_fornecedor(self, id_fornecedor: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[Fornecedor]:
        """
        Atualizar fornecedor existente com validação de empresa.
        
        Args:
            id_fornecedor: ID do fornecedor
            data: Dados para atualização
            id_empresa: ID da empresa para verificação
            
        Returns:
            Fornecedor atualizado ou None se não encontrado
        """
        if 'cnpj' in data:
            # Verificar duplicação de CNPJ na mesma empresa
            existente = await self.get_by_cnpj_empresa(
                cnpj=data['cnpj'],
                id_empresa=id_empresa
            )
            
            if existente and existente.id_fornecedor != id_fornecedor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um fornecedor com CNPJ '{data['cnpj']}' nesta empresa"
                )
                
        return await self.update(id_fornecedor, data, id_empresa)
        
    async def create_fornecedor(self, data: Dict[str, Any]) -> Fornecedor:
        """
        Criar novo fornecedor com validação de duplicidade.
        
        Args:
            data: Dados do fornecedor a ser criado
            
        Returns:
            Novo fornecedor criado
        """
        # Verificar duplicação de CNPJ na mesma empresa
        existente = await self.get_by_cnpj_empresa(
            cnpj=data['cnpj'],
            id_empresa=data['id_empresa']
        )
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um fornecedor com CNPJ '{data['cnpj']}' nesta empresa"
            )
            
        return await self.create(data) 