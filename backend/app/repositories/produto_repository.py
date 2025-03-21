from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_, func
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutosPaginados
from app.utils.logging_config import get_logger
from app.repositories.base_repository import BaseRepository

# Configurar logger
logger = get_logger(__name__)

class ProdutoRepository(BaseRepository[Produto, ProdutoCreate, ProdutoUpdate]):
    """Repositório para operações com produtos."""
    
    def __init__(self):
        """Inicializa o repositório com o modelo Produto."""
        super().__init__(Produto)
    
    def get(self, db: Session, id: UUID) -> Optional[Produto]:
        """
        Obtém um produto pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID do produto
            
        Returns:
            Produto: Produto encontrado ou None
        """
        return db.query(Produto).filter(Produto.id_produto == id).first()
    
    def get_by_empresa(self, db: Session, id_empresa: UUID) -> List[Produto]:
        """
        Obtém todos os produtos de uma empresa.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: ID da empresa
            
        Returns:
            List[Produto]: Lista de produtos da empresa
        """
        return db.query(Produto).filter(Produto.id_empresa == id_empresa).all()
    
    def get_by_codigo(self, db: Session, codigo: str, id_empresa: UUID) -> Optional[Produto]:
        """
        Obtém um produto pelo código dentro de uma empresa específica.
        
        Args:
            db: Sessão do banco de dados
            codigo: Código do produto
            id_empresa: ID da empresa
            
        Returns:
            Produto: Produto encontrado ou None
        """
        return db.query(Produto).filter(
            Produto.codigo == codigo,
            Produto.id_empresa == id_empresa
        ).first()
    
    def get_by_codigo_barras(self, db: Session, codigo_barras: str, id_empresa: UUID) -> Optional[Produto]:
        """
        Obtém um produto pelo código de barras dentro de uma empresa específica.
        
        Args:
            db: Sessão do banco de dados
            codigo_barras: Código de barras do produto
            id_empresa: ID da empresa
            
        Returns:
            Produto: Produto encontrado ou None
        """
        return db.query(Produto).filter(
            Produto.codigo_barras == codigo_barras,
            Produto.id_empresa == id_empresa
        ).first()
    
    def get_by_categoria(self, db: Session, id_categoria: UUID) -> List[Produto]:
        """
        Obtém todos os produtos de uma categoria.
        
        Args:
            db: Sessão do banco de dados
            id_categoria: ID da categoria
            
        Returns:
            List[Produto]: Lista de produtos da categoria
        """
        return db.query(Produto).filter(Produto.id_categoria == id_categoria).all()
    
    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        id_categoria: Optional[UUID] = None,
        ativo: Optional[bool] = None,
        estoque_baixo: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Produto]:
        """
        Obtém múltiplos produtos com paginação e filtragem opcional.
        
        Args:
            db: Sessão do banco de dados
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            id_categoria: Filtrar por categoria específica
            ativo: Filtrar por status (ativo/inativo)
            estoque_baixo: Filtrar produtos com estoque abaixo do mínimo
            filters: Filtros adicionais
            
        Returns:
            List[Produto]: Lista de produtos
        """
        query = db.query(Produto)
        
        # Filtrar por empresa se fornecido
        if id_empresa:
            query = query.filter(Produto.id_empresa == id_empresa)
        
        # Filtrar por categoria se fornecido
        if id_categoria:
            query = query.filter(Produto.id_categoria == id_categoria)
        
        # Filtrar por status se fornecido
        if ativo is not None:
            query = query.filter(Produto.ativo == ativo)
        
        # Filtrar produtos com estoque abaixo do mínimo
        if estoque_baixo:
            query = query.filter(Produto.estoque_atual <= Produto.estoque_minimo)
        
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(Produto.nome.ilike(termo_busca))
                del filters["nome"]  # Remove para não processar novamente
            
            # Busca por código ou código de barras
            if "codigo" in filters and filters["codigo"]:
                termo_busca = f"%{filters['codigo']}%"
                query = query.filter(
                    or_(
                        Produto.codigo.ilike(termo_busca),
                        Produto.codigo_barras.ilike(termo_busca)
                    )
                )
                del filters["codigo"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value and hasattr(Produto, field):
                    if isinstance(value, str):
                        query = query.filter(getattr(Produto, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(Produto, field) == value)
        
        # Ordenar por nome
        query = query.order_by(Produto.nome)
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(
        self, 
        db: Session, 
        id_empresa: Optional[UUID] = None,
        id_categoria: Optional[UUID] = None,
        ativo: Optional[bool] = None,
        estoque_baixo: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Obtém a contagem total de produtos com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            id_empresa: Filtrar por empresa específica
            id_categoria: Filtrar por categoria específica
            ativo: Filtrar por status (ativo/inativo)
            estoque_baixo: Filtrar produtos com estoque abaixo do mínimo
            filters: Filtros adicionais
            
        Returns:
            int: Contagem de produtos
        """
        query = db.query(func.count(Produto.id_produto))
        
        # Filtrar por empresa se fornecido
        if id_empresa:
            query = query.filter(Produto.id_empresa == id_empresa)
        
        # Filtrar por categoria se fornecido
        if id_categoria:
            query = query.filter(Produto.id_categoria == id_categoria)
        
        # Filtrar por status se fornecido
        if ativo is not None:
            query = query.filter(Produto.ativo == ativo)
        
        # Filtrar produtos com estoque abaixo do mínimo
        if estoque_baixo:
            query = query.filter(Produto.estoque_atual <= Produto.estoque_minimo)
        
        if filters:
            # Tratamento especial para busca por nome
            if "nome" in filters and filters["nome"]:
                termo_busca = f"%{filters['nome']}%"
                query = query.filter(Produto.nome.ilike(termo_busca))
                del filters["nome"]  # Remove para não processar novamente
            
            # Busca por código ou código de barras
            if "codigo" in filters and filters["codigo"]:
                termo_busca = f"%{filters['codigo']}%"
                query = query.filter(
                    or_(
                        Produto.codigo.ilike(termo_busca),
                        Produto.codigo_barras.ilike(termo_busca)
                    )
                )
                del filters["codigo"]  # Remove para não processar novamente
            
            # Processamento dos demais filtros
            for field, value in filters.items():
                if value and hasattr(Produto, field):
                    if isinstance(value, str):
                        query = query.filter(getattr(Produto, field).ilike(f"%{value}%"))
                    else:
                        query = query.filter(getattr(Produto, field) == value)
        
        return query.scalar()
    
    def create(self, db: Session, *, obj_in: ProdutoCreate) -> Produto:
        """
        Cria um novo produto.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados do produto
            
        Returns:
            Produto: Produto criado
            
        Raises:
            HTTPException: Se o código ou código de barras já estiver em uso
        """
        # Verificar se o código já existe para esta empresa (se fornecido)
        if obj_in.codigo:
            existing = self.get_by_codigo(db, obj_in.codigo, obj_in.id_empresa)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código já cadastrado para outro produto desta empresa"
                )
        
        # Verificar se o código de barras já existe para esta empresa (se fornecido)
        if obj_in.codigo_barras:
            existing = self.get_by_codigo_barras(db, obj_in.codigo_barras, obj_in.id_empresa)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código de barras já cadastrado para outro produto desta empresa"
                )
        
        # Criar objeto de dados
        db_obj = Produto(
            id_empresa=obj_in.id_empresa,
            id_categoria=obj_in.id_categoria,
            nome=obj_in.nome,
            descricao=obj_in.descricao,
            codigo=obj_in.codigo,
            codigo_barras=obj_in.codigo_barras,
            valor_compra=obj_in.valor_compra,
            valor_venda=obj_in.valor_venda,
            estoque_atual=obj_in.estoque_atual,
            estoque_minimo=obj_in.estoque_minimo,
            ativo=obj_in.ativo,
            imagens=obj_in.imagens
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Produto,
        obj_in: ProdutoUpdate
    ) -> Produto:
        """
        Atualiza um produto existente.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto produto existente
            obj_in: Dados para atualizar
            
        Returns:
            Produto: Produto atualizado
            
        Raises:
            HTTPException: Se o código ou código de barras já estiver em uso por outro produto
        """
        # Verificar se o código está sendo alterado e já existe
        if obj_in.codigo and obj_in.codigo != db_obj.codigo:
            existing = self.get_by_codigo(db, obj_in.codigo, db_obj.id_empresa)
            if existing and existing.id_produto != db_obj.id_produto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código já cadastrado para outro produto desta empresa"
                )
        
        # Verificar se o código de barras está sendo alterado e já existe
        if obj_in.codigo_barras and obj_in.codigo_barras != db_obj.codigo_barras:
            existing = self.get_by_codigo_barras(db, obj_in.codigo_barras, db_obj.id_empresa)
            if existing and existing.id_produto != db_obj.id_produto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código de barras já cadastrado para outro produto desta empresa"
                )
        
        # Atualizar os campos
        if obj_in.nome is not None:
            db_obj.nome = obj_in.nome
        if obj_in.descricao is not None:
            db_obj.descricao = obj_in.descricao
        if obj_in.codigo is not None:
            db_obj.codigo = obj_in.codigo
        if obj_in.codigo_barras is not None:
            db_obj.codigo_barras = obj_in.codigo_barras
        if obj_in.valor_compra is not None:
            db_obj.valor_compra = obj_in.valor_compra
        if obj_in.valor_venda is not None:
            db_obj.valor_venda = obj_in.valor_venda
        if obj_in.estoque_atual is not None:
            db_obj.estoque_atual = obj_in.estoque_atual
        if obj_in.estoque_minimo is not None:
            db_obj.estoque_minimo = obj_in.estoque_minimo
        if obj_in.ativo is not None:
            db_obj.ativo = obj_in.ativo
        if obj_in.imagens is not None:
            db_obj.imagens = obj_in.imagens
        if obj_in.id_categoria is not None:
            db_obj.id_categoria = obj_in.id_categoria
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def atualizar_estoque(
        self,
        db: Session,
        *,
        id_produto: UUID,
        quantidade: float,
        is_entrada: bool = True
    ) -> Produto:
        """
        Atualiza o estoque de um produto.
        
        Args:
            db: Sessão do banco de dados
            id_produto: ID do produto
            quantidade: Quantidade a ser ajustada
            is_entrada: Se True, adiciona ao estoque; se False, subtrai
            
        Returns:
            Produto: Produto atualizado
            
        Raises:
            HTTPException: Se o produto não for encontrado
        """
        produto = self.get(db, id=id_produto)
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Atualizar estoque
        if is_entrada:
            produto.estoque_atual += quantidade
        else:
            if produto.estoque_atual < quantidade:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Estoque insuficiente para operação"
                )
            produto.estoque_atual -= quantidade
        
        db.add(produto)
        db.commit()
        db.refresh(produto)
        
        return produto

    @staticmethod
    def get_all(
        db: Session, 
        id_empresa: UUID, 
        skip: int = 0, 
        limit: int = 100,
        nome: Optional[str] = None,
        codigo: Optional[str] = None,
        categoria: Optional[str] = None,
        ativo: Optional[bool] = None,
        order_by: str = "nome",
        order_direction: str = "asc"
    ) -> ProdutosPaginados:
        """
        Retorna todos os produtos com filtros e paginação
        """
        # Consulta base
        query = db.query(Produto).filter(Produto.id_empresa == id_empresa)
        
        # Aplicar filtros
        if nome:
            query = query.filter(Produto.nome.ilike(f"%{nome}%"))
        if codigo:
            query = query.filter(Produto.codigo.ilike(f"%{codigo}%"))
        if categoria:
            query = query.filter(Produto.categoria.ilike(f"%{categoria}%"))
        if ativo is not None:
            query = query.filter(Produto.ativo == ativo)
        
        # Calcular total para paginação
        total = query.count()
        
        # Aplicar ordenação
        order_column = getattr(Produto, order_by, Produto.nome)
        if order_direction.lower() == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
        
        # Aplicar paginação
        query = query.offset(skip).limit(limit)
        
        # Calcular páginas
        pages = (total + limit - 1) // limit if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1
        
        # Retornar resultados paginados
        return ProdutosPaginados(
            items=query.all(),
            total=total,
            page=page,
            size=limit,
            pages=pages
        )

    @staticmethod
    def update_estoque(db: Session, id_produto: UUID, id_empresa: UUID, quantidade: Decimal) -> Optional[Produto]:
        """
        Atualiza o estoque de um produto
        """
        # Obter produto existente
        db_produto = ProdutoRepository.get_by_id(db, id_produto, id_empresa)
        
        if not db_produto:
            logger.warning(
                f"Tentativa de atualizar estoque de produto inexistente: {id_produto}",
                extra={"id_empresa": str(id_empresa)}
            )
            return None
        
        # Calcular novo estoque
        novo_estoque = db_produto.estoque_atual + quantidade
        
        # Validar se estoque ficará negativo
        if novo_estoque < 0:
            logger.warning(
                f"Tentativa de ajustar estoque para valor negativo: {novo_estoque}",
                extra={"id_empresa": str(id_empresa), "id_produto": str(id_produto)}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque não pode ficar negativo"
            )
        
        # Atualizar estoque
        db_produto.estoque_atual = novo_estoque
        
        try:
            db.add(db_produto)
            db.commit()
            db.refresh(db_produto)
            logger.info(
                f"Estoque atualizado com sucesso para {db_produto.estoque_atual}",
                extra={
                    "id_empresa": str(id_empresa), 
                    "id_produto": str(id_produto),
                    "alteracao": float(quantidade)
                }
            )
            return db_produto
        except Exception as e:
            db.rollback()
            logger.error(
                f"Erro ao atualizar estoque: {str(e)}",
                extra={"id_empresa": str(id_empresa), "id_produto": str(id_produto)}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar estoque"
            )

    @staticmethod
    def delete(db: Session, id_produto: UUID, id_empresa: UUID) -> bool:
        """
        Exclui um produto
        """
        # Obter produto existente
        db_produto = ProdutoRepository.get_by_id(db, id_produto, id_empresa)
        
        if not db_produto:
            logger.warning(
                f"Tentativa de excluir produto inexistente: {id_produto}",
                extra={"id_empresa": str(id_empresa)}
            )
            return False
        
        try:
            db.delete(db_produto)
            db.commit()
            logger.info(
                f"Produto excluído com sucesso: {db_produto.nome} ({db_produto.codigo})",
                extra={"id_empresa": str(id_empresa), "id_produto": str(id_produto)}
            )
            return True
        except Exception as e:
            db.rollback()
            logger.error(
                f"Erro ao excluir produto: {str(e)}",
                extra={"id_empresa": str(id_empresa), "id_produto": str(id_produto)}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao excluir produto"
            ) 