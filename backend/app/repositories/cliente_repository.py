"""Repositório para operações de banco de dados relacionadas a clientes."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.repositories.base_repository import BaseRepository


class ClienteRepository(BaseRepository[Cliente, ClienteCreate, ClienteUpdate]):
    """Repositório para operações com clientes."""
    
    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão e modelo."""
        self.session = session
        super().__init__(Cliente)
    
    async def get_by_id(self, id_cliente: UUID, id_empresa: UUID = None) -> Optional[Cliente]:
        """
        Buscar cliente pelo ID e empresa.
        
        Args:
            id_cliente: ID do cliente
            id_empresa: ID da empresa para validação
            
        Returns:
            Cliente se encontrado, None caso contrário
        """
        query = select(Cliente).where(Cliente.id_cliente == id_cliente)
        
        if id_empresa:
            query = query.where(Cliente.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_cpf_cnpj_empresa(self, cpf_cnpj: str, id_empresa: UUID) -> Optional[Cliente]:
        """
        Buscar cliente pelo CPF/CNPJ e empresa.
        
        Args:
            cpf_cnpj: CPF ou CNPJ do cliente
            id_empresa: ID da empresa
            
        Returns:
            Cliente se encontrado, None caso contrário
        """
        query = select(Cliente).where(
            Cliente.cpf_cnpj == cpf_cnpj,
            Cliente.id_empresa == id_empresa
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_with_filters(
        self, 
        skip: int = 0, 
        limit: int = 100,
        id_empresa: UUID = None,
        **filters
    ) -> Tuple[List[Cliente], int]:
        """
        Listar clientes com paginação e filtros.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: ID da empresa para filtrar
            **filters: Filtros adicionais (nome, cpf_cnpj, ativo, etc)
            
        Returns:
            Tuple[List[Cliente], int]: Lista de clientes e contagem total
        """
        # Consulta para a lista de clientes
        query = select(Cliente)
        
        # Consulta para contagem total
        count_query = select(func.count()).select_from(Cliente)
        
        # Aplicar filtro de empresa
        if id_empresa:
            query = query.where(Cliente.id_empresa == id_empresa)
            count_query = count_query.where(Cliente.id_empresa == id_empresa)
        
        # Aplicar filtros específicos
        if "nome" in filters and filters["nome"]:
            termo_busca = f"%{filters['nome']}%"
            query = query.where(Cliente.nome.ilike(termo_busca))
            count_query = count_query.where(Cliente.nome.ilike(termo_busca))
        
        if "cpf_cnpj" in filters and filters["cpf_cnpj"]:
            termo_busca = f"%{filters['cpf_cnpj']}%"
            query = query.where(Cliente.cpf_cnpj.ilike(termo_busca))
            count_query = count_query.where(Cliente.cpf_cnpj.ilike(termo_busca))
        
        if "ativo" in filters and filters["ativo"] is not None:
            query = query.where(Cliente.ativo == filters["ativo"])
            count_query = count_query.where(Cliente.ativo == filters["ativo"])
        
        # Aplicar ordenação
        query = query.order_by(Cliente.nome.asc())
        
        # Executar consulta de contagem
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one() or 0
        
        # Aplicar paginação e executar consulta principal
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        clientes = result.scalars().all()
        
        return list(clientes), total
    
    async def create(self, data: Dict[str, Any]) -> Cliente:
        """
        Criar novo cliente.
        
        Args:
            data: Dados do cliente
            
        Returns:
            Cliente: Cliente criado
        """
        # Aproveitar a implementação do BaseRepository
        return await super().create(data, data.get("id_empresa"))
    
    async def update(self, id_cliente: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[Cliente]:
        """
        Atualizar cliente existente.
        
        Args:
            id_cliente: ID do cliente
            data: Dados para atualização
            id_empresa: ID da empresa para validação
            
        Returns:
            Cliente: Cliente atualizado ou None se não encontrado
        """
        # Primeiro verificar se o cliente existe e pertence à empresa
        cliente = await self.get_by_id(id_cliente, id_empresa)
        if not cliente:
            return None
            
        # Preparar os dados para atualização
        data_copy = data.copy()
        data_copy.pop("id_empresa", None)  # Remover id_empresa se existir
        
        # Atualizar os campos do cliente
        for key, value in data_copy.items():
            if hasattr(cliente, key):
                setattr(cliente, key, value)
                
        # Salvar as alterações
        await self.session.commit()
        await self.session.refresh(cliente)
        
        return cliente
    
    async def delete(self, id_cliente: UUID, id_empresa: UUID) -> bool:
        """
        Excluir cliente.
        
        Args:
            id_cliente: ID do cliente
            id_empresa: ID da empresa para validação
            
        Returns:
            bool: True se excluído com sucesso, False caso contrário
        """
        # Verificar se o cliente existe e pertence à empresa
        cliente = await self.get_by_id(id_cliente, id_empresa)
        if not cliente:
            return False
            
        # Excluir o cliente (ou marcar como inativo)
        # Opção 1: Exclusão física
        await self.session.delete(cliente)
        
        # Opção 2: Exclusão lógica (marcar como inativo)
        # cliente.ativo = False
        
        # Salvar alterações
        await self.session.commit()
        
        return True

    async def get_by_entity_id(self, id: UUID) -> Optional[Cliente]:
        """
        Obtém um cliente pelo ID.
        
        Args:
            id: ID do cliente
            
        Returns:
            Cliente: Cliente encontrado ou None
        """
        query = select(Cliente).where(Cliente.id_cliente == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_empresa(self, id_empresa: UUID) -> List[Cliente]:
        """
        Obtém todos os clientes de uma empresa.
        
        Args:
            id_empresa: ID da empresa
            
        Returns:
            List[Cliente]: Lista de clientes da empresa
        """
        query = select(Cliente).where(Cliente.id_empresa == id_empresa)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Cliente]:
        """
        Obtém múltiplos clientes com paginação e filtragem opcional.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            filters: Filtros adicionais
            
        Returns:
            List[Cliente]: Lista de clientes
        """
        query = select(Cliente)
        
        # Filtrar por empresa se fornecido
        if id_empresa:
            query = query.where(Cliente.id_empresa == id_empresa)
        
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(Cliente.nome.ilike(termo_busca))
            
            # Tratamento para busca por cpf_cnpj
            if "cpf_cnpj" in filters and filters["cpf_cnpj"]:
                termo_busca = f"%{filters['cpf_cnpj']}%"
                query = query.where(Cliente.cpf_cnpj.ilike(termo_busca))
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Cliente, field) and field not in ["nome", "cpf_cnpj"]:
                    query = query.where(getattr(Cliente, field) == value)
        
        # Ordenar por nome
        query = query.order_by(Cliente.nome)
        
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
        Obtém a contagem total de clientes com filtros opcionais.
        
        Args:
            id_empresa: Filtrar por empresa específica
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de clientes
        """
        query = select(func.count()).select_from(Cliente)
        
        # Filtrar por empresa se fornecido
        if id_empresa:
            query = query.where(Cliente.id_empresa == id_empresa)
        
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(Cliente.nome.ilike(termo_busca))
            
            # Tratamento para busca por cpf_cnpj
            if "cpf_cnpj" in filters and filters["cpf_cnpj"]:
                termo_busca = f"%{filters['cpf_cnpj']}%"
                query = query.where(Cliente.cpf_cnpj.ilike(termo_busca))
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(Cliente, field) and field not in ["nome", "cpf_cnpj"]:
                    query = query.where(getattr(Cliente, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one() or 0 