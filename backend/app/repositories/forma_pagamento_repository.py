"""Repositório para operações com formas de pagamento."""
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status

from app.models.forma_pagamento import FormaPagamento
from app.models.lancamento import Lancamento
from app.schemas.forma_pagamento import FormaPagamentoCreate, FormaPagamentoUpdate
from app.repositories.base_repository import BaseRepository


class FormaPagamentoRepository(BaseRepository[FormaPagamento, FormaPagamentoCreate, FormaPagamentoUpdate]):
    """Repositório para operações com formas de pagamento."""
    
    def __init__(self):
        """Inicializa o repositório com o modelo FormaPagamento."""
        super().__init__(FormaPagamento)
    
    def get(self, db: Session, id: UUID) -> Optional[FormaPagamento]:
        """
        Obtém uma forma de pagamento pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID da forma de pagamento
            
        Returns:
            FormaPagamento: Forma de pagamento encontrada ou None
        """
        return db.query(FormaPagamento).filter(FormaPagamento.id_forma == id).first()
    
    def get_by_nome(
        self, 
        db: Session, 
        nome: str,
        id_empresa: UUID
    ) -> Optional[FormaPagamento]:
        """
        Obtém uma forma de pagamento pelo nome.
        
        Args:
            db: Sessão do banco de dados
            nome: Nome da forma de pagamento
            id_empresa: ID da empresa
            
        Returns:
            FormaPagamento: Forma de pagamento encontrada ou None
        """
        return db.query(FormaPagamento).filter(
            FormaPagamento.nome == nome,
            FormaPagamento.id_empresa == id_empresa
        ).first()
    
    def get_by_empresa(
        self, 
        db: Session, 
        id_empresa: UUID,
        ativa: Optional[bool] = None
    ) -> List[FormaPagamento]:
        """
        Obtém todas as formas de pagamento de uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            ativa: Filtrar por status de ativação
            
        Returns:
            List[FormaPagamento]: Lista de formas de pagamento da empresa
        """
        query = db.query(FormaPagamento).filter(FormaPagamento.id_empresa == id_empresa)
        
        if ativa is not None:
            query = query.filter(FormaPagamento.ativa == ativa)
            
        return query.order_by(FormaPagamento.nome).all()
    
    def get_multi(
        self,
        db: Session,
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
            db: Sessão do banco de dados
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            ativa: Filtrar por status de ativação
            filters: Filtros adicionais
            
        Returns:
            List[FormaPagamento]: Lista de formas de pagamento
        """
        query = db.query(FormaPagamento)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(FormaPagamento.id_empresa == id_empresa)
            
        if ativa is not None:
            query = query.filter(FormaPagamento.ativa == ativa)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(FormaPagamento.nome.ilike(termo_busca))
                del filters["nome"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(FormaPagamento, field):
                    query = query.filter(getattr(FormaPagamento, field) == value)
        
        # Ordenação padrão por nome
        query = query.order_by(FormaPagamento.nome)
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self, 
        db: Session, 
        id_empresa: Optional[UUID] = None,
        ativa: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de formas de pagamento com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: Filtrar por empresa específica
            ativa: Filtrar por status de ativação
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de formas de pagamento
        """
        query = db.query(FormaPagamento)
        
        # Aplicar filtros principais
        if id_empresa:
            query = query.filter(FormaPagamento.id_empresa == id_empresa)
            
        if ativa is not None:
            query = query.filter(FormaPagamento.ativa == ativa)
        
        # Filtros adicionais
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(FormaPagamento.nome.ilike(termo_busca))
                del filters["nome"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value is not None and hasattr(FormaPagamento, field):
                    query = query.filter(getattr(FormaPagamento, field) == value)
        
        return query.count()
    
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: FormaPagamentoCreate
    ) -> FormaPagamento:
        """
        Cria uma nova forma de pagamento.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados da forma de pagamento
            
        Returns:
            FormaPagamento: Forma de pagamento criada
            
        Raises:
            HTTPException: Se já existir uma forma de pagamento com o mesmo nome
        """
        # Verificar se já existe forma de pagamento com o mesmo nome
        forma_existente = self.get_by_nome(db, obj_in.nome, obj_in.id_empresa)
        if forma_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma forma de pagamento com este nome para esta empresa"
            )
        
        # Criar objeto forma de pagamento
        db_obj = FormaPagamento(**obj_in.dict())
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: FormaPagamento,
        obj_in: FormaPagamentoUpdate
    ) -> FormaPagamento:
        """
        Atualiza uma forma de pagamento existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto forma de pagamento existente
            obj_in: Dados para atualizar
            
        Returns:
            FormaPagamento: Forma de pagamento atualizada
            
        Raises:
            HTTPException: Se o novo nome já estiver em uso
        """
        # Verificar se está alterando o nome e se o novo nome já existe
        update_data = obj_in.dict(exclude_unset=True)
        
        if "nome" in update_data and update_data["nome"] != db_obj.nome:
            forma_existente = self.get_by_nome(db, update_data["nome"], db_obj.id_empresa)
            if forma_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma forma de pagamento com este nome para esta empresa"
                )
        
        # Atualizar campos
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def remove(self, db: Session, *, id: UUID) -> FormaPagamento:
        """
        Remove uma forma de pagamento.
        
        Args:
            db: Sessão do banco de dados
            id: ID da forma de pagamento
            
        Returns:
            FormaPagamento: Forma de pagamento removida
            
        Raises:
            HTTPException: Se a forma de pagamento não for encontrada ou tiver lançamentos associados
        """
        forma = db.query(FormaPagamento).filter(FormaPagamento.id_forma == id).first()
        if not forma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forma de pagamento não encontrada"
            )
        
        # Verificar se existem lançamentos utilizando esta forma de pagamento
        lancamentos = db.query(Lancamento).filter(
            Lancamento.id_forma_pagamento == id
        ).count()
        
        if lancamentos > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível excluir esta forma de pagamento pois ela está sendo utilizada em {lancamentos} lançamento(s)"
            )
        
        db.delete(forma)
        db.commit()
        
        return forma
    
    def toggle_ativa(self, db: Session, *, id: UUID) -> FormaPagamento:
        """
        Alterna o status de ativação da forma de pagamento.
        
        Args:
            db: Sessão do banco de dados
            id: ID da forma de pagamento
            
        Returns:
            FormaPagamento: Forma de pagamento atualizada
            
        Raises:
            HTTPException: Se a forma de pagamento não for encontrada
        """
        forma = db.query(FormaPagamento).filter(FormaPagamento.id_forma == id).first()
        if not forma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forma de pagamento não encontrada"
            )
        
        forma.ativa = not forma.ativa
        
        db.add(forma)
        db.commit()
        db.refresh(forma)
        
        return forma 