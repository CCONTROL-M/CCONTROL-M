"""Repositório para operações com empresas."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate
from app.repositories.base_repository import BaseRepository


class EmpresaRepository(BaseRepository[Empresa, EmpresaCreate, EmpresaUpdate]):
    """Repositório para operações com empresas."""
    
    def __init__(self):
        """Inicializa o repositório com o modelo Empresa."""
        super().__init__(Empresa)
    
    def get(self, db: Session, id: UUID) -> Optional[Empresa]:
        """
        Obtém uma empresa pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID da empresa
            
        Returns:
            Empresa: Empresa encontrada ou None
        """
        return db.query(Empresa).filter(Empresa.id_empresa == id).first()
    
    def get_by_cnpj(self, db: Session, cnpj: str) -> Optional[Empresa]:
        """
        Obtém uma empresa pelo CNPJ.
        
        Args:
            db: Sessão do banco de dados
            cnpj: CNPJ da empresa
            
        Returns:
            Empresa: Empresa encontrada ou None
        """
        return db.query(Empresa).filter(Empresa.cnpj == cnpj).first()
    
    def get_by_field(self, db: Session, field_name: str, value: Any) -> Optional[Empresa]:
        """
        Obtém uma empresa pelo valor de um campo específico.
        
        Args:
            db: Sessão do banco de dados
            field_name: Nome do campo
            value: Valor do campo
            
        Returns:
            Empresa: Empresa encontrada ou None
        """
        return db.query(Empresa).filter(getattr(Empresa, field_name) == value).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Empresa]:
        """
        Obtém múltiplas empresas com paginação e filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            skip: Registros para pular
            limit: Limite de registros
            filters: Filtros adicionais (nome, cidade, etc)
            
        Returns:
            List[Empresa]: Lista de empresas
        """
        query = db.query(Empresa)
        
        if filters:
            # Tratamento especial para busca por nome (razão social ou fantasia)
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(
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
                        query = query.filter(getattr(Empresa, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(Empresa, field) == value)
        
        # Ordenar por razão social
        query = query.order_by(Empresa.razao_social)
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Obtém a contagem total de empresas com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de empresas
        """
        query = db.query(Empresa)
        
        if filters:
            # Tratamento especial para busca por nome (razão social ou fantasia)
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(
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
                        query = query.filter(getattr(Empresa, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(Empresa, field) == value)
        
        return query.count()
    
    def create(self, db: Session, *, obj_in: EmpresaCreate) -> Empresa:
        """
        Cria uma nova empresa.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados da empresa
            
        Returns:
            Empresa: Empresa criada
            
        Raises:
            HTTPException: Se o CNPJ já estiver em uso
        """
        # Verificar se o CNPJ já existe
        if self.get_by_cnpj(db, obj_in.cnpj):
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
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Empresa,
        obj_in: EmpresaUpdate
    ) -> Empresa:
        """
        Atualiza uma empresa existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto empresa existente
            obj_in: Dados para atualizar
            
        Returns:
            Empresa: Empresa atualizada
            
        Raises:
            HTTPException: Se o CNPJ já estiver em uso por outra empresa
        """
        # Verificar se o CNPJ está sendo alterado e já existe
        if obj_in.cnpj and obj_in.cnpj != db_obj.cnpj:
            empresa_com_cnpj = self.get_by_cnpj(db, obj_in.cnpj)
            if empresa_com_cnpj and empresa_com_cnpj.id_empresa != db_obj.id_empresa:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CNPJ já está em uso por outra empresa"
                )
        
        # Atualizar os campos
        if obj_in.razao_social is not None:
            db_obj.razao_social = obj_in.razao_social
        if obj_in.nome_fantasia is not None:
            db_obj.nome_fantasia = obj_in.nome_fantasia
        if obj_in.cnpj is not None:
            db_obj.cnpj = obj_in.cnpj
        if obj_in.email is not None:
            db_obj.email = obj_in.email
        if obj_in.telefone is not None:
            db_obj.telefone = obj_in.telefone
        if obj_in.endereco is not None:
            db_obj.endereco = obj_in.endereco
        if obj_in.cidade is not None:
            db_obj.cidade = obj_in.cidade
        if obj_in.estado is not None:
            db_obj.estado = obj_in.estado
        if obj_in.logo_url is not None:
            db_obj.logo_url = obj_in.logo_url
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj 