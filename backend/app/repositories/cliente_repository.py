"""Repositório para operações de banco de dados relacionadas a clientes."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.repositories.base_repository import BaseRepository


class ClienteRepository(BaseRepository[Cliente, ClienteCreate, ClienteUpdate]):
    """Repositório para operações com clientes."""
    
    def __init__(self, session: AsyncSession):
        """Inicializar repositório com sessão e modelo."""
        super().__init__(session, Cliente)
    
    def get(self, db: Session, id: UUID) -> Optional[Cliente]:
        """
        Obtém um cliente pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID do cliente
            
        Returns:
            Cliente: Cliente encontrado ou None
        """
        return db.query(Cliente).filter(Cliente.id_cliente == id).first()
    
    def get_by_empresa(self, db: Session, id_empresa: UUID) -> List[Cliente]:
        """
        Obtém todos os clientes de uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            
        Returns:
            List[Cliente]: Lista de clientes da empresa
        """
        return db.query(Cliente).filter(Cliente.id_empresa == id_empresa).all()
    
    def get_by_cpf_cnpj(self, db: Session, cpf_cnpj: str, id_empresa: UUID) -> Optional[Cliente]:
        """
        Obtém um cliente pelo CPF/CNPJ dentro de uma empresa específica.
        
        Args:
            db: Sessão do banco de dados
            cpf_cnpj: CPF/CNPJ do cliente
            id_empresa: ID da empresa
            
        Returns:
            Cliente: Cliente encontrado ou None
        """
        return db.query(Cliente).filter(
            Cliente.cpf_cnpj == cpf_cnpj,
            Cliente.id_empresa == id_empresa
        ).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Cliente]:
        """
        Obtém múltiplos clientes com paginação e filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            filters: Filtros adicionais
            
        Returns:
            List[Cliente]: Lista de clientes
        """
        query = db.query(Cliente)
        
        # Filtrar por empresa se fornecido
        if id_empresa:
            query = query.filter(Cliente.id_empresa == id_empresa)
        
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(Cliente.nome.ilike(termo_busca))
                del filters["nome"]  # Remove para não processar novamente
            
            # Tratamento para busca por cpf_cnpj
            if "cpf_cnpj" in filters and filters["cpf_cnpj"]:
                termo_busca = f"%{filters['cpf_cnpj']}%"
                query = query.filter(Cliente.cpf_cnpj.ilike(termo_busca))
                del filters["cpf_cnpj"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value and hasattr(Cliente, field):
                    query = query.filter(getattr(Cliente, field) == value)
        
        # Ordenar por nome
        query = query.order_by(Cliente.nome)
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self, 
        db: Session, 
        id_empresa: Optional[UUID] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de clientes com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: Filtrar por empresa específica
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de clientes
        """
        query = db.query(Cliente)
        
        # Filtrar por empresa se fornecido
        if id_empresa:
            query = query.filter(Cliente.id_empresa == id_empresa)
        
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(Cliente.nome.ilike(termo_busca))
                del filters["nome"]  # Remove para não processar novamente
            
            # Tratamento para busca por cpf_cnpj
            if "cpf_cnpj" in filters and filters["cpf_cnpj"]:
                termo_busca = f"%{filters['cpf_cnpj']}%"
                query = query.filter(Cliente.cpf_cnpj.ilike(termo_busca))
                del filters["cpf_cnpj"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value and hasattr(Cliente, field):
                    query = query.filter(getattr(Cliente, field) == value)
        
        return query.count()
    
    def create(self, db: Session, *, obj_in: ClienteCreate) -> Cliente:
        """
        Cria um novo cliente.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados do cliente
            
        Returns:
            Cliente: Cliente criado
        """
        # Verificar se o CPF/CNPJ já existe para esta empresa (se fornecido)
        if obj_in.cpf_cnpj:
            existing = self.get_by_cpf_cnpj(db, obj_in.cpf_cnpj, obj_in.id_empresa)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF/CNPJ já cadastrado para outro cliente desta empresa"
                )
        
        # Criar objeto de dados
        db_obj = Cliente(
            id_empresa=obj_in.id_empresa,
            nome=obj_in.nome,
            cpf_cnpj=obj_in.cpf_cnpj,
            contato=obj_in.contato
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Cliente,
        obj_in: ClienteUpdate
    ) -> Cliente:
        """
        Atualiza um cliente existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto cliente existente
            obj_in: Dados para atualizar
            
        Returns:
            Cliente: Cliente atualizado
            
        Raises:
            HTTPException: Se o CPF/CNPJ já estiver em uso por outro cliente
        """
        # Verificar se o CPF/CNPJ está sendo alterado e já existe
        if obj_in.cpf_cnpj and obj_in.cpf_cnpj != db_obj.cpf_cnpj:
            existing = self.get_by_cpf_cnpj(db, obj_in.cpf_cnpj, db_obj.id_empresa)
            if existing and existing.id_cliente != db_obj.id_cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF/CNPJ já cadastrado para outro cliente desta empresa"
                )
        
        # Atualizar os campos
        if obj_in.nome is not None:
            db_obj.nome = obj_in.nome
        if obj_in.cpf_cnpj is not None:
            db_obj.cpf_cnpj = obj_in.cpf_cnpj
        if obj_in.contato is not None:
            db_obj.contato = obj_in.contato
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj

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
        return result.scalars().first()

    async def list_with_filters(
        self, 
        skip: int = 0, 
        limit: int = 100,
        id_empresa: UUID = None,
        nome: Optional[str] = None,
        cpf_cnpj: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> tuple[List[Cliente], int]:
        """
        Listar clientes com filtros e paginação.
        
        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            id_empresa: ID da empresa para filtrar
            nome: Filtrar por nome
            cpf_cnpj: Filtrar por CPF/CNPJ
            ativo: Filtrar por status
            
        Returns:
            Lista de clientes e contagem total
        """
        filters = []
        
        if id_empresa:
            filters.append(Cliente.id_empresa == id_empresa)
        
        if nome:
            filters.append(Cliente.nome.ilike(f"%{nome}%"))
            
        if cpf_cnpj:
            filters.append(Cliente.cpf_cnpj.ilike(f"%{cpf_cnpj}%"))
            
        if ativo is not None:
            filters.append(Cliente.ativo == ativo)
            
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def update_cliente(self, id_cliente: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[Cliente]:
        """
        Atualizar cliente existente com validação de empresa.
        
        Args:
            id_cliente: ID do cliente
            data: Dados para atualização
            id_empresa: ID da empresa para verificação
            
        Returns:
            Cliente atualizado ou None se não encontrado
        """
        if 'cpf_cnpj' in data:
            # Verificar duplicação de CPF/CNPJ na mesma empresa
            existente = await self.get_by_cpf_cnpj_empresa(
                cpf_cnpj=data['cpf_cnpj'],
                id_empresa=id_empresa
            )
            
            if existente and existente.id_cliente != id_cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um cliente com CPF/CNPJ '{data['cpf_cnpj']}' nesta empresa"
                )
                
        return await self.update(id_cliente, data, id_empresa)
        
    async def create_cliente(self, data: Dict[str, Any]) -> Cliente:
        """
        Criar novo cliente com validação de duplicidade.
        
        Args:
            data: Dados do cliente a ser criado
            
        Returns:
            Novo cliente criado
        """
        # Verificar duplicação de CPF/CNPJ na mesma empresa
        existente = await self.get_by_cpf_cnpj_empresa(
            cpf_cnpj=data['cpf_cnpj'],
            id_empresa=data['id_empresa']
        )
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um cliente com CPF/CNPJ '{data['cpf_cnpj']}' nesta empresa"
            )
            
        return await self.create(data) 