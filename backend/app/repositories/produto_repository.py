from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, or_, update, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoList
from app.utils.logging_config import get_logger
from app.repositories.base_repository import BaseRepository
from app.database import db_session

# Configurar logger
logger = get_logger(__name__)

class ProdutoRepository(BaseRepository[Produto, ProdutoCreate, ProdutoUpdate]):
    """Repositório para operações com produtos."""
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa o repositório com o modelo Produto e a sessão.
        
        Args:
            session: Sessão assíncrona do SQLAlchemy
        """
        self.session = session
        super().__init__(Produto)
    
    async def get_by_id(self, id_produto: UUID, id_empresa: Optional[UUID] = None) -> Optional[Produto]:
        """
        Obtém um produto pelo ID.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa para validação
            
        Returns:
            Produto: Produto encontrado ou None
        """
        query = select(Produto).where(Produto.id_produto == id_produto)
        
        if id_empresa:
            query = query.where(Produto.id_empresa == id_empresa)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_empresa(self, id_empresa: UUID) -> List[Produto]:
        """
        Obtém todos os produtos de uma empresa.
        
        Args:
            id_empresa: ID da empresa
            
        Returns:
            List[Produto]: Lista de produtos da empresa
        """
        query = select(Produto).where(Produto.id_empresa == id_empresa)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_codigo(self, codigo: str, id_empresa: UUID) -> Optional[Produto]:
        """
        Obtém um produto pelo código dentro de uma empresa específica.
        
        Args:
            codigo: Código do produto
            id_empresa: ID da empresa
            
        Returns:
            Produto: Produto encontrado ou None
        """
        query = select(Produto).where(
            Produto.codigo == codigo,
            Produto.id_empresa == id_empresa
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_codigo_barras(self, codigo_barras: str, id_empresa: UUID) -> Optional[Produto]:
        """
        Obtém um produto pelo código de barras dentro de uma empresa específica.
        
        Args:
            codigo_barras: Código de barras do produto
            id_empresa: ID da empresa
            
        Returns:
            Produto: Produto encontrado ou None
        """
        query = select(Produto).where(
            Produto.codigo_barras == codigo_barras,
            Produto.id_empresa == id_empresa
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_categoria(self, id_categoria: UUID) -> List[Produto]:
        """
        Obtém todos os produtos de uma categoria.
        
        Args:
            id_categoria: ID da categoria
            
        Returns:
            List[Produto]: Lista de produtos da categoria
        """
        query = select(Produto).where(Produto.id_categoria == id_categoria)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        id_empresa: Optional[UUID] = None,
        id_categoria: Optional[UUID] = None,
        ativo: Optional[bool] = None,
        estoque_baixo: Optional[bool] = None,
        **filters
    ) -> Tuple[List[Produto], int]:
        """
        Obtém múltiplos produtos com paginação e filtragem opcional.
        
        Args:
            skip: Registros para pular
            limit: Limite de registros
            id_empresa: Filtrar por empresa específica
            id_categoria: Filtrar por categoria específica
            ativo: Filtrar por status (ativo/inativo)
            estoque_baixo: Filtrar produtos com estoque abaixo do mínimo
            **filters: Filtros adicionais
            
        Returns:
            Tuple[List[Produto], int]: Lista de produtos e contagem total
        """
        # Consulta para a lista de produtos
        query = select(Produto)
        
        # Consulta para contagem total
        count_query = select(func.count()).select_from(Produto)
        
        # Aplicar filtros comuns a ambas consultas
        if id_empresa:
            query = query.where(Produto.id_empresa == id_empresa)
            count_query = count_query.where(Produto.id_empresa == id_empresa)
        
        if id_categoria:
            query = query.where(Produto.id_categoria == id_categoria)
            count_query = count_query.where(Produto.id_categoria == id_categoria)
        
        if ativo is not None:
            query = query.where(Produto.ativo == ativo)
            count_query = count_query.where(Produto.ativo == ativo)
        
        if estoque_baixo:
            query = query.where(Produto.estoque_atual <= Produto.estoque_minimo)
            count_query = count_query.where(Produto.estoque_atual <= Produto.estoque_minimo)
        
        # Filtros para busca por nome ou código
        if "nome" in filters and filters["nome"]:
            termo_busca = f"%{filters['nome']}%"
            query = query.where(Produto.nome.ilike(termo_busca))
            count_query = count_query.where(Produto.nome.ilike(termo_busca))
        
        if "codigo" in filters and filters["codigo"]:
            termo_busca = f"%{filters['codigo']}%"
            query = query.where(or_(
                Produto.codigo.ilike(termo_busca),
                Produto.codigo_barras.ilike(termo_busca)
            ))
            count_query = count_query.where(or_(
                Produto.codigo.ilike(termo_busca),
                Produto.codigo_barras.ilike(termo_busca)
            ))
        
        # Aplicar ordenação - o padrão é por nome
        order_by = filters.get("order_by", "nome")
        order_direction = filters.get("order_direction", "asc")
        
        if hasattr(Produto, order_by):
            column = getattr(Produto, order_by)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        else:
            # Ordenação padrão por nome ascendente
            query = query.order_by(Produto.nome)
        
        # Executar consulta de contagem
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one() or 0
        
        # Aplicar paginação e executar consulta principal
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        produtos = result.scalars().all()
        
        return list(produtos), total
    
    async def create(self, data: Dict[str, Any]) -> Produto:
        """
        Cria um novo produto.
        
        Args:
            data: Dados do produto a ser criado
            
        Returns:
            Produto: Produto criado
            
        Raises:
            HTTPException: Se houver erro na criação ou duplicidade
        """
        # Verificar duplicação de código dentro da mesma empresa
        if "codigo" in data and data["codigo"] and "id_empresa" in data:
            existente = await self.get_by_codigo(data["codigo"], data["id_empresa"])
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um produto com código '{data['codigo']}' nesta empresa"
                )
        
        # Verificar duplicação de código de barras dentro da mesma empresa
        if "codigo_barras" in data and data["codigo_barras"] and "id_empresa" in data:
            existente = await self.get_by_codigo_barras(data["codigo_barras"], data["id_empresa"])
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um produto com código de barras '{data['codigo_barras']}' nesta empresa"
                )
                
        # Aproveitar a implementação do BaseRepository
        return await super().create(data, data.get("id_empresa"))
    
    async def update(self, id_produto: UUID, data: Dict[str, Any], id_empresa: UUID) -> Optional[Produto]:
        """
        Atualiza um produto existente.
        
        Args:
            id_produto: ID do produto
            data: Dados para atualização
            id_empresa: ID da empresa para validação
            
        Returns:
            Produto: Produto atualizado ou None se não encontrado
            
        Raises:
            HTTPException: Se houver erro na atualização ou duplicidade
        """
        # Verificar se o produto existe e pertence à empresa
        produto = await self.get_by_id(id_produto, id_empresa)
        if not produto:
            return None
        
        # Verificar duplicação de código se estiver sendo modificado
        if "codigo" in data and data["codigo"] and data["codigo"] != produto.codigo:
            existente = await self.get_by_codigo(data["codigo"], id_empresa)
            if existente and existente.id_produto != id_produto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um produto com código '{data['codigo']}' nesta empresa"
                )
        
        # Verificar duplicação de código de barras se estiver sendo modificado
        if "codigo_barras" in data and data["codigo_barras"] and data["codigo_barras"] != produto.codigo_barras:
            existente = await self.get_by_codigo_barras(data["codigo_barras"], id_empresa)
            if existente and existente.id_produto != id_produto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um produto com código de barras '{data['codigo_barras']}' nesta empresa"
                )
        
        # Preparar os dados para atualização
        data_copy = data.copy()
        data_copy.pop("id_empresa", None)  # Remover id_empresa se existir
        
        # Construir a consulta de atualização
        stmt = (
            select(Produto)
            .where(Produto.id_produto == id_produto)
            .where(Produto.id_empresa == id_empresa)
        )
        
        result = await self.session.execute(stmt)
        produto = result.scalar_one_or_none()
        
        if not produto:
            return None
            
        # Atualizar os atributos do produto
        for key, value in data_copy.items():
            if hasattr(produto, key):
                setattr(produto, key, value)
        
        # Salvar as alterações
        self.session.add(produto)
        await self.session.commit()
        await self.session.refresh(produto)
        
        return produto
    
    async def update_estoque(self, id_produto: UUID, id_empresa: UUID, quantidade: Decimal, is_entrada: bool = True) -> Optional[Produto]:
        """
        Atualiza o estoque de um produto.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa para validação
            quantidade: Quantidade a ajustar (positivo)
            is_entrada: Se True, adiciona ao estoque; se False, subtrai
            
        Returns:
            Produto: Produto com estoque atualizado ou None se não encontrado
            
        Raises:
            HTTPException: Se houver erro na atualização
        """
        # Verificar se o produto existe e pertence à empresa
        produto = await self.get_by_id(id_produto, id_empresa)
        if not produto:
            return None
        
        # Calcular novo estoque
        novo_estoque = produto.estoque_atual
        if is_entrada:
            novo_estoque += float(quantidade)
        else:
            novo_estoque -= float(quantidade)
            if novo_estoque < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Estoque não pode ficar negativo"
                )
        
        # Atualizar o estoque
        produto.estoque_atual = novo_estoque
        
        # Salvar as alterações
        self.session.add(produto)
        await self.session.commit()
        await self.session.refresh(produto)
        
        return produto
    
    async def delete(self, id_produto: UUID, id_empresa: UUID) -> bool:
        """
        Remove um produto.
        
        Args:
            id_produto: ID do produto
            id_empresa: ID da empresa para validação
            
        Returns:
            bool: True se removido com sucesso
            
        Raises:
            HTTPException: Se o produto não existir ou não pertencer à empresa
        """
        # Verificar se o produto existe e pertence à empresa
        produto = await self.get_by_id(id_produto, id_empresa)
        if not produto:
            return False
        
        # Remover o produto
        await self.session.delete(produto)
        await self.session.commit()
        
        return True 