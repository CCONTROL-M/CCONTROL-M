"""Repositório para operações com usuários."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.repositories.base_repository import BaseRepository
from app.utils.security import get_password_hash


class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    """Repositório para operações com usuários."""
    
    def __init__(self):
        """Inicializa o repositório com o modelo Usuario."""
        super().__init__(Usuario)
    
    def get(self, db: Session, id: UUID) -> Optional[Usuario]:
        """
        Obtém um usuário pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID do usuário
            
        Returns:
            Usuario: Usuário encontrado ou None
        """
        return db.query(Usuario).filter(Usuario.id_usuario == id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[Usuario]:
        """
        Obtém um usuário pelo email.
        
        Args:
            db: Sessão do banco de dados
            email: Email do usuário
            
        Returns:
            Usuario: Usuário encontrado ou None
        """
        return db.query(Usuario).filter(Usuario.email == email).first()
    
    def get_by_field(self, db: Session, field_name: str, value: Any) -> Optional[Usuario]:
        """
        Obtém um usuário pelo valor de um campo específico.
        
        Args:
            db: Sessão do banco de dados
            field_name: Nome do campo
            value: Valor do campo
            
        Returns:
            Usuario: Usuário encontrado ou None
        """
        return db.query(Usuario).filter(getattr(Usuario, field_name) == value).first()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Usuario]:
        """
        Obtém múltiplos usuários com paginação e filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            skip: Registros para pular
            limit: Limite de registros
            filters: Filtros adicionais
            
        Returns:
            List[Usuario]: Lista de usuários
        """
        query = db.query(Usuario)
        
        if filters:
            for field, value in filters.items():
                if hasattr(Usuario, field):
                    if field == "nome" or field == "email":
                        # Busca por substring para campos de texto
                        query = query.filter(getattr(Usuario, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(Usuario, field) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: UsuarioCreate) -> Usuario:
        """
        Cria um novo usuário.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados do usuário
            
        Returns:
            Usuario: Usuário criado
            
        Raises:
            HTTPException: Se o email já estiver em uso
        """
        # Verificar se o email já existe
        if self.get_by_email(db, obj_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso por outro usuário"
            )
        
        # Criar objeto de dados com senha hasheada
        db_obj = Usuario(
            id_empresa=obj_in.id_empresa,
            nome=obj_in.nome,
            email=obj_in.email,
            senha_hash=get_password_hash(obj_in.senha),
            tipo_usuario=obj_in.tipo_usuario,
            telas_permitidas=obj_in.telas_permitidas
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Usuario,
        obj_in: UsuarioUpdate
    ) -> Usuario:
        """
        Atualiza um usuário existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto usuário existente
            obj_in: Dados para atualizar
            
        Returns:
            Usuario: Usuário atualizado
            
        Raises:
            HTTPException: Se o email já estiver em uso por outro usuário
        """
        # Verificar se o email está sendo alterado e já existe
        if obj_in.email and obj_in.email != db_obj.email:
            usuario_com_email = self.get_by_email(db, obj_in.email)
            if usuario_com_email and usuario_com_email.id_usuario != db_obj.id_usuario:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já está em uso por outro usuário"
                )
        
        # Atualizar os campos
        if obj_in.nome is not None:
            db_obj.nome = obj_in.nome
        if obj_in.email is not None:
            db_obj.email = obj_in.email
        if obj_in.tipo_usuario is not None:
            db_obj.tipo_usuario = obj_in.tipo_usuario
        if obj_in.telas_permitidas is not None:
            db_obj.telas_permitidas = obj_in.telas_permitidas
        if obj_in.senha is not None:
            db_obj.senha_hash = get_password_hash(obj_in.senha)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj 