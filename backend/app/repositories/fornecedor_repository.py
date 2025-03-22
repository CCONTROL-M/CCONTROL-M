"""Repositório para operações de banco de dados relacionadas a fornecedores."""
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fornecedor import Fornecedor
from app.repositories.base_repository import BaseRepository


class FornecedorRepository(BaseRepository[Fornecedor, Dict[str, Any], Dict[str, Any]]):
    """Repositório para operações com fornecedores."""

    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão e modelo."""
        self.session = session
        super().__init__(Fornecedor)

    async def get_by_id(self, id_fornecedor: UUID, id_empresa: Optional[UUID] = None) -> Optional[Fornecedor]:
        """
        Buscar fornecedor pelo ID.
        
        Args:
            id_fornecedor: ID do fornecedor
            id_empresa: ID da empresa para validação (opcional)
            
        Returns:
            Fornecedor se encontrado, None caso contrário
        """
        query = select(Fornecedor).where(Fornecedor.id_fornecedor == id_fornecedor)
        
        if id_empresa:
            query = query.where(Fornecedor.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_entity_id(self, id: UUID) -> Optional[Fornecedor]:
        """
        Obtém um fornecedor pelo ID.
        
        Args:
            id: ID do fornecedor
            
        Returns:
            Fornecedor: Fornecedor encontrado ou None
        """
        query = select(Fornecedor).where(Fornecedor.id_fornecedor == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

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
        return result.scalar_one_or_none()

    async def get_by_empresa(self, id_empresa: UUID) -> List[Fornecedor]:
        """
        Obtém todos os fornecedores de uma empresa.
        
        Args:
            id_empresa: ID da empresa
            
        Returns:
            List[Fornecedor]: Lista de fornecedores da empresa
        """
        query = select(Fornecedor).where(Fornecedor.id_empresa == id_empresa)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_with_filters(
        self, 
        skip: int = 0, 
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        **filters
    ) -> Tuple[List[Fornecedor], int]:
        """
        Listar fornecedores com paginação e filtros.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: ID da empresa para filtrar
            **filters: Filtros adicionais (nome, cnpj, ativo, etc)
            
        Returns:
            Tuple[List[Fornecedor], int]: Lista de fornecedores e contagem total
        """
        # Consulta para lista de fornecedores
        query = select(Fornecedor)
        
        # Consulta para contagem
        count_query = select(func.count()).select_from(Fornecedor)
        
        # Aplicar filtro de empresa
        if id_empresa:
            query = query.where(Fornecedor.id_empresa == id_empresa)
            count_query = count_query.where(Fornecedor.id_empresa == id_empresa)
        
        # Aplicar filtros específicos
        if "nome" in filters and filters["nome"]:
            termo_busca = f"%{filters['nome']}%"
            query = query.where(Fornecedor.nome.ilike(termo_busca))
            count_query = count_query.where(Fornecedor.nome.ilike(termo_busca))
        
        if "cnpj" in filters and filters["cnpj"]:
            termo_busca = f"%{filters['cnpj']}%"
            query = query.where(Fornecedor.cnpj.ilike(termo_busca))
            count_query = count_query.where(Fornecedor.cnpj.ilike(termo_busca))
        
        if "email" in filters and filters["email"]:
            termo_busca = f"%{filters['email']}%"
            query = query.where(Fornecedor.email.ilike(termo_busca))
            count_query = count_query.where(Fornecedor.email.ilike(termo_busca))
        
        if "telefone" in filters and filters["telefone"]:
            termo_busca = f"%{filters['telefone']}%"
            query = query.where(Fornecedor.telefone.ilike(termo_busca))
            count_query = count_query.where(Fornecedor.telefone.ilike(termo_busca))
        
        if "ativo" in filters and filters["ativo"] is not None:
            query = query.where(Fornecedor.ativo == filters["ativo"])
            count_query = count_query.where(Fornecedor.ativo == filters["ativo"])
        
        # Ordenar por nome
        query = query.order_by(Fornecedor.nome.asc())
        
        # Executar consulta de contagem
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one() or 0
        
        # Aplicar paginação e executar consulta principal
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        fornecedores = result.scalars().all()
        
        return list(fornecedores), total

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Fornecedor]:
        """
        Obtém múltiplos fornecedores com paginação e filtragem opcional.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            filters: Filtros adicionais
            
        Returns:
            List[Fornecedor]: Lista de fornecedores
        """
        query = select(Fornecedor)
        
        # Filtrar por empresa se fornecido
        if id_empresa:
            query = query.where(Fornecedor.id_empresa == id_empresa)
        
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(Fornecedor.nome.ilike(termo_busca))
            
            # Tratamento para busca por cnpj
            if "cnpj" in filters and filters["cnpj"]:
                termo_busca = f"%{filters['cnpj']}%"
                query = query.where(Fornecedor.cnpj.ilike(termo_busca))
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Fornecedor, field) and field not in ["nome", "cnpj"]:
                    query = query.where(getattr(Fornecedor, field) == value)
        
        # Ordenar por nome
        query = query.order_by(Fornecedor.nome)
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_count(
        self,
        id_empresa: Optional[UUID] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de fornecedores com filtros opcionais.
        
        Args:
            id_empresa: Filtrar por empresa específica
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de fornecedores
        """
        query = select(func.count()).select_from(Fornecedor)
        
        # Filtrar por empresa se fornecido
        if id_empresa:
            query = query.where(Fornecedor.id_empresa == id_empresa)
        
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(Fornecedor.nome.ilike(termo_busca))
            
            # Tratamento para busca por cnpj
            if "cnpj" in filters and filters["cnpj"]:
                termo_busca = f"%{filters['cnpj']}%"
                query = query.where(Fornecedor.cnpj.ilike(termo_busca))
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Fornecedor, field) and field not in ["nome", "cnpj"]:
                    query = query.where(getattr(Fornecedor, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one() or 0
        
    async def create(self, data: Dict[str, Any]) -> Fornecedor:
        """
        Criar novo fornecedor.
        
        Args:
            data: Dados do fornecedor
            
        Returns:
            Fornecedor criado
        """
        fornecedor = Fornecedor(**data)
        self.session.add(fornecedor)
        await self.session.flush()
        return fornecedor
        
    async def update(self, id_fornecedor: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[Fornecedor]:
        """
        Atualizar fornecedor existente.
        
        Args:
            id_fornecedor: ID do fornecedor
            data: Dados para atualização
            id_empresa: ID da empresa para validação
            
        Returns:
            Fornecedor atualizado ou None se não encontrado
        """
        # Primeiro verificar se o fornecedor existe
        fornecedor = await self.get_by_id(id_fornecedor, id_empresa)
        if not fornecedor:
            return None
                
        # Atualizar campos
        for key, value in data.items():
            if hasattr(fornecedor, key):
                setattr(fornecedor, key, value)
        
        # Salvar alterações
        self.session.add(fornecedor)
        await self.session.flush()
        
        return fornecedor
    
    async def delete(self, id_fornecedor: UUID, id_empresa: UUID) -> bool:
        """
        Excluir fornecedor pelo ID.
        
        Args:
            id_fornecedor: ID do fornecedor
            id_empresa: ID da empresa para validação
            
        Returns:
            bool: True se removido com sucesso
        """
        # Verificar se o fornecedor existe
        fornecedor = await self.get_by_id(id_fornecedor, id_empresa)
        
        if not fornecedor:
            return False
        
        # Excluir fornecedor
        await self.session.delete(fornecedor)
        await self.session.flush()
        
        return True
    
    async def commit(self):
        """Persistir alterações no banco de dados."""
        await self.session.commit()
    
    async def rollback(self):
        """Reverter alterações pendentes."""
        await self.session.rollback() 