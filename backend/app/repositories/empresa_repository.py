"""Repositório para operações com empresas."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate


class EmpresaRepository:
    """Repositório para operações com empresas."""
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa o repositório com a sessão do banco de dados.
        
        Args:
            session: Sessão assíncrona do banco de dados
        """
        self.session = session
    
    @classmethod
    async def get_by_id(cls, session: AsyncSession, id_empresa: UUID) -> Optional[Empresa]:
        """
        Obtém uma empresa pelo ID (método estático).
        
        Args:
            session: Sessão do banco de dados
            id_empresa: ID da empresa
            
        Returns:
            Empresa: Empresa encontrada ou None
        """
        query = select(Empresa).where(Empresa.id_empresa == id_empresa)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id_instance(self, id_empresa: UUID) -> Optional[Empresa]:
        """
        Obtém uma empresa pelo ID.
        
        Args:
            id_empresa: ID da empresa
            
        Returns:
            Empresa: Empresa encontrada ou None
        """
        query = select(Empresa).where(Empresa.id_empresa == id_empresa)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_cnpj(self, cnpj: str) -> Optional[Empresa]:
        """
        Obtém uma empresa pelo CNPJ.
        
        Args:
            cnpj: CNPJ da empresa
            
        Returns:
            Empresa: Empresa encontrada ou None
        """
        query = select(Empresa).where(Empresa.cnpj == cnpj)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_field(self, field_name: str, value: Any) -> Optional[Empresa]:
        """
        Obtém uma empresa pelo valor de um campo específico.
        
        Args:
            field_name: Nome do campo
            value: Valor do campo
            
        Returns:
            Empresa: Empresa encontrada ou None
        """
        query = select(Empresa).where(getattr(Empresa, field_name) == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Empresa], int]:
        """
        Obtém múltiplas empresas com paginação e filtragem opcional.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            filters: Filtros adicionais (nome, cidade, etc)
            
        Returns:
            Tuple[List[Empresa], int]: Lista de empresas e contagem total
        """
        query = select(Empresa)
        count_query = select(func.count()).select_from(Empresa)
        
        if filters:
            # Tratamento especial para busca por nome (razão social ou fantasia)
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                nome_filter = or_(
                    Empresa.razao_social.ilike(termo_busca),
                    Empresa.nome_fantasia.ilike(termo_busca)
                )
                query = query.where(nome_filter)
                count_query = count_query.where(nome_filter)
                del filters["nome"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value and hasattr(Empresa, field):
                    if field in ["razao_social", "nome_fantasia", "cidade", "estado"]:
                        # Busca por substring para campos de texto
                        field_filter = getattr(Empresa, field).ilike(f"%{value}%")
                    else:
                        field_filter = getattr(Empresa, field) == value
                    
                    query = query.where(field_filter)
                    count_query = count_query.where(field_filter)
        
        # Ordenar por razão social
        query = query.order_by(Empresa.razao_social)
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Executar as queries
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        
        return items, total
    
    async def get_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Obtém a contagem total de empresas com filtros opcionais.
        
        Args:
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de empresas
        """
        query = select(func.count()).select_from(Empresa)
        
        if filters:
            # Tratamento especial para busca por nome (razão social ou fantasia)
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.where(
                    or_(
                        Empresa.razao_social.ilike(termo_busca),
                        Empresa.nome_fantasia.ilike(termo_busca)
                    )
                )
                del filters["nome"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value and hasattr(Empresa, field):
                    if field in ["razao_social", "nome_fantasia", "cidade", "estado"]:
                        # Busca por substring para campos de texto
                        query = query.where(getattr(Empresa, field).ilike(f"%{value}%"))
                    else:
                        query = query.where(getattr(Empresa, field) == value)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def create(self, obj_in: EmpresaCreate) -> Empresa:
        """
        Cria uma nova empresa.
        
        Args:
            obj_in: Dados da empresa
            
        Returns:
            Empresa: Empresa criada
            
        Raises:
            HTTPException: Se o CNPJ já estiver em uso
        """
        try:
            # Verificar se o CNPJ já existe
            existing_empresa = await self.get_by_cnpj(obj_in.cnpj)
            if existing_empresa:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CNPJ já está em uso por outra empresa"
                )
            
            # Criar objeto de dados
            db_obj = Empresa(
                razao_social=obj_in.razao_social,
                nome_fantasia=obj_in.nome_fantasia,
                cnpj=obj_in.cnpj,
                email=obj_in.email,
                telefone=obj_in.telefone,
                endereco=obj_in.endereco,
                cidade=obj_in.cidade,
                estado=obj_in.estado,
                logo_url=obj_in.logo_url
            )
            
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return db_obj
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar empresa: {str(e)}"
            )
    
    async def update(
        self,
        id_empresa: UUID,
        obj_in: EmpresaUpdate
    ) -> Empresa:
        """
        Atualiza uma empresa existente.
        
        Args:
            id_empresa: ID da empresa a ser atualizada
            obj_in: Dados para atualizar
            
        Returns:
            Empresa: Empresa atualizada
            
        Raises:
            HTTPException: Se o CNPJ já estiver em uso por outra empresa
            HTTPException: Se a empresa não for encontrada
        """
        try:
            # Buscar empresa existente
            db_obj = await self.get_by_id_instance(id_empresa)
            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Empresa não encontrada"
                )
            
            # Verificar se o CNPJ está sendo alterado e já existe
            if obj_in.cnpj and obj_in.cnpj != db_obj.cnpj:
                empresa_com_cnpj = await self.get_by_cnpj(obj_in.cnpj)
                if empresa_com_cnpj and empresa_com_cnpj.id_empresa != db_obj.id_empresa:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="CNPJ já está em uso por outra empresa"
                    )
            
            # Atualizar os campos
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            await self.session.commit()
            await self.session.refresh(db_obj)
            
            return db_obj
        except HTTPException:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar empresa: {str(e)}"
            )
    
    async def delete(self, id_empresa: UUID) -> bool:
        """
        Remove uma empresa.
        
        Args:
            id_empresa: ID da empresa a ser removida
            
        Returns:
            bool: True se a empresa foi removida com sucesso
            
        Raises:
            HTTPException: Se a empresa não for encontrada
        """
        try:
            db_obj = await self.get_by_id_instance(id_empresa)
            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Empresa não encontrada"
                )
            
            await self.session.delete(db_obj)
            await self.session.commit()
            
            return True
        except HTTPException:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao excluir empresa: {str(e)}"
            ) 