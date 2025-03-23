"""Serviço para gerenciamento de categorias no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
import logging
from datetime import datetime

from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.lancamento_repository import LancamentoRepository
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.database import get_async_session
from app.models.categoria import Categoria as CategoriaModel
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService


# Configurar logger
logger = logging.getLogger(__name__)


class CategoriaService:
    """Serviço para gerenciamento de categorias."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 log_service: LogSistemaService = Depends(),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = CategoriaRepository(session)
        self.lancamento_repository = LancamentoRepository(session)
        self.log_service = log_service
        self.auditoria_service = auditoria_service
        self.logger = logger
        
    async def get_categoria(self, id_categoria: UUID, id_empresa: UUID) -> Categoria:
        """
        Obter categoria pelo ID.
        
        Args:
            id_categoria: ID da categoria
            id_empresa: ID da empresa para validação de acesso
            
        Returns:
            Categoria encontrada
            
        Raises:
            HTTPException: Se a categoria não for encontrada
        """
        self.logger.info(f"Buscando categoria ID: {id_categoria}")
        
        categoria = await self.repository.get_by_id(id_categoria, id_empresa)
        if not categoria:
            self.logger.warning(f"Categoria não encontrada: {id_categoria}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        return categoria
        
    async def listar_categorias(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        tipo: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Tuple[List[Categoria], int]:
        """
        Listar categorias com paginação e filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            nome: Filtrar por nome
            tipo: Filtrar por tipo (RECEITA ou DESPESA)
            ativo: Filtrar por status ativo
            
        Returns:
            Lista de categorias e contagem total
        """
        self.logger.info(f"Buscando categorias com filtros: empresa={id_empresa}, nome={nome}, tipo={tipo}")
        
        filters = [{"id_empresa": id_empresa}]
        
        if nome:
            filters.append({"nome__ilike": f"%{nome}%"})
            
        if tipo:
            filters.append({"tipo": tipo})
            
        if ativo is not None:
            filters.append({"ativo": ativo})
            
        return await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
    async def criar_categoria(self, categoria: CategoriaCreate, id_usuario: UUID) -> Categoria:
        """
        Criar nova categoria.
        
        Args:
            categoria: Dados da categoria a ser criada
            id_usuario: ID do usuário que está criando a categoria
            
        Returns:
            Categoria criada
            
        Raises:
            HTTPException: Se ocorrer um erro na validação
        """
        self.logger.info(f"Criando nova categoria: {categoria.nome}, tipo: {categoria.tipo}")
        
        # Verificar se já existe categoria com mesmo nome e tipo na empresa
        categoria_existente = await self.repository.get_by_nome_tipo(
            nome=categoria.nome, 
            tipo=categoria.tipo, 
            id_empresa=categoria.id_empresa
        )
        if categoria_existente:
            self.logger.warning(
                f"Já existe uma categoria com o nome '{categoria.nome}' e tipo '{categoria.tipo}' na empresa"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma categoria com o nome '{categoria.nome}' e tipo '{categoria.tipo}'"
            )
            
        # Criar categoria
        try:
            categoria_data = categoria.model_dump()
            
            # Definir como ativo por padrão se não especificado
            if "ativo" not in categoria_data or categoria_data["ativo"] is None:
                categoria_data["ativo"] = True
                
            nova_categoria = await self.repository.create(categoria_data)
            
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=categoria.id_empresa,
                    id_usuario=id_usuario,
                    acao="criar_categoria",
                    descricao=f"Categoria criada: {nova_categoria.nome}, tipo: {nova_categoria.tipo}",
                    dados={
                        "id_categoria": str(nova_categoria.id_categoria), 
                        "nome": nova_categoria.nome,
                        "tipo": nova_categoria.tipo
                    }
                )
            )
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="CRIAR_CATEGORIA",
                detalhes={
                    "id_categoria": str(nova_categoria.id_categoria),
                    "nome": nova_categoria.nome,
                    "tipo": nova_categoria.tipo
                },
                empresa_id=categoria.id_empresa
            )
            
            return nova_categoria
        except Exception as e:
            self.logger.error(f"Erro ao criar categoria: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar categoria"
            )
        
    async def atualizar_categoria(self, id_categoria: UUID, categoria: CategoriaUpdate, id_empresa: UUID, id_usuario: UUID) -> Categoria:
        """
        Atualizar categoria existente.
        
        Args:
            id_categoria: ID da categoria a ser atualizada
            categoria: Dados para atualização
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está atualizando a categoria
            
        Returns:
            Categoria atualizada
            
        Raises:
            HTTPException: Se a categoria não for encontrada ou ocorrer erro na validação
        """
        self.logger.info(f"Atualizando categoria: {id_categoria}")
        
        # Verificar se a categoria existe
        categoria_atual = await self.get_categoria(id_categoria, id_empresa)
        
        # Verificar unicidade do nome e tipo se estiver sendo atualizado
        update_data = {k: v for k, v in categoria.model_dump().items() if v is not None}
        
        tipo_atualizado = update_data.get('tipo', categoria_atual.tipo)
        nome_atualizado = update_data.get('nome', categoria_atual.nome)
        
        if nome_atualizado or tipo_atualizado:
            categoria_existente = await self.repository.get_by_nome_tipo(
                nome=nome_atualizado, 
                tipo=tipo_atualizado, 
                id_empresa=id_empresa
            )
            if categoria_existente and categoria_existente.id_categoria != id_categoria:
                self.logger.warning(
                    f"Já existe uma categoria com o nome '{nome_atualizado}' e tipo '{tipo_atualizado}' na empresa"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe uma categoria com o nome '{nome_atualizado}' e tipo '{tipo_atualizado}'"
                )
                
        # Atualizar categoria
        try:
            categoria_atualizada = await self.repository.update(id_categoria, update_data, id_empresa)
            
            if not categoria_atualizada:
                self.logger.warning(f"Categoria não encontrada após tentativa de atualização: {id_categoria}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoria não encontrada"
                )
                
            # Registrar log
            await self.log_service.registrar_log(
                LogSistemaCreate(
                    id_empresa=id_empresa,
                    id_usuario=id_usuario,
                    acao="atualizar_categoria",
                    descricao=f"Categoria atualizada: {categoria_atualizada.nome}",
                    dados={
                        "id_categoria": str(id_categoria),
                        "atualizacoes": update_data
                    }
                )
            )
            
            # Registrar ação
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="ATUALIZAR_CATEGORIA",
                detalhes={
                    "id_categoria": str(id_categoria),
                    "alteracoes": update_data
                },
                empresa_id=id_empresa
            )
            
            return categoria_atualizada
        except Exception as e:
            self.logger.error(f"Erro ao atualizar categoria: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar categoria"
            )
            
    async def ativar_categoria(self, id_categoria: UUID, id_empresa: UUID, id_usuario: UUID) -> Categoria:
        """
        Ativar uma categoria.
        
        Args:
            id_categoria: ID da categoria a ser ativada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está ativando a categoria
            
        Returns:
            Categoria ativada
            
        Raises:
            HTTPException: Se a categoria não for encontrada
        """
        self.logger.info(f"Ativando categoria: {id_categoria}")
        
        # Verificar se a categoria existe
        categoria = await self.get_categoria(id_categoria, id_empresa)
        
        # Verificar se já está ativa
        if categoria.ativo:
            self.logger.warning(f"Categoria já está ativa: {id_categoria}")
            return categoria
            
        # Ativar categoria
        update_data = {"ativo": True}
        
        categoria_atualizada = await self.repository.update(id_categoria, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="ativar_categoria",
                descricao=f"Categoria ativada: {categoria.nome}",
                dados={"id_categoria": str(id_categoria)}
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="ATIVAR_CATEGORIA",
            detalhes={"id_categoria": str(id_categoria)},
            empresa_id=id_empresa
        )
        
        return categoria_atualizada
        
    async def desativar_categoria(self, id_categoria: UUID, id_empresa: UUID, id_usuario: UUID) -> Categoria:
        """
        Desativar uma categoria.
        
        Args:
            id_categoria: ID da categoria a ser desativada
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está desativando a categoria
            
        Returns:
            Categoria desativada
            
        Raises:
            HTTPException: Se a categoria não for encontrada
        """
        self.logger.info(f"Desativando categoria: {id_categoria}")
        
        # Verificar se a categoria existe
        categoria = await self.get_categoria(id_categoria, id_empresa)
        
        # Verificar se já está inativa
        if not categoria.ativo:
            self.logger.warning(f"Categoria já está inativa: {id_categoria}")
            return categoria
            
        # Desativar categoria
        update_data = {"ativo": False}
        
        categoria_atualizada = await self.repository.update(id_categoria, update_data, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="desativar_categoria",
                descricao=f"Categoria desativada: {categoria.nome}",
                dados={"id_categoria": str(id_categoria)}
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="DESATIVAR_CATEGORIA",
            detalhes={"id_categoria": str(id_categoria)},
            empresa_id=id_empresa
        )
        
        return categoria_atualizada
        
    async def remover_categoria(self, id_categoria: UUID, id_empresa: UUID, id_usuario: UUID) -> Dict[str, Any]:
        """
        Remover categoria pelo ID.
        
        Args:
            id_categoria: ID da categoria a ser removida
            id_empresa: ID da empresa para validação de acesso
            id_usuario: ID do usuário que está removendo a categoria
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se a categoria não for encontrada ou não puder ser removida
        """
        self.logger.info(f"Removendo categoria: {id_categoria}")
        
        # Verificar se a categoria existe
        categoria = await self.get_categoria(id_categoria, id_empresa)
        
        # Verificar se tem lançamentos associados
        tem_lancamentos = await self.lancamento_repository.has_by_categoria(id_categoria, id_empresa)
        if tem_lancamentos:
            self.logger.warning(f"Categoria possui lançamentos associados: {id_categoria}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover uma categoria com lançamentos associados"
            )
            
        # Remover categoria
        await self.repository.delete(id_categoria, id_empresa)
        
        # Registrar log
        await self.log_service.registrar_log(
            LogSistemaCreate(
                id_empresa=id_empresa,
                id_usuario=id_usuario,
                acao="remover_categoria",
                descricao=f"Categoria removida: {categoria.nome}",
                dados={
                    "id_categoria": str(id_categoria), 
                    "nome": categoria.nome,
                    "tipo": categoria.tipo
                }
            )
        )
        
        # Registrar ação
        await self.auditoria_service.registrar_acao(
            usuario_id=id_usuario,
            acao="EXCLUIR_CATEGORIA",
            detalhes={
                "id_categoria": str(id_categoria),
                "nome": categoria.nome,
                "tipo": categoria.tipo
            },
            empresa_id=id_empresa
        )
        
        return {"detail": f"Categoria '{categoria.nome}' removida com sucesso"}

    async def get_multi(
        self,
        empresa_id: UUID,
        skip: int = 0,
        limit: int = 100,
        tipo: Optional[str] = None,
        status: Optional[str] = None,
        busca: Optional[str] = None
    ) -> PaginatedResponse[Categoria]:
        """
        Buscar múltiplas categorias com filtros.
        
        Args:
            empresa_id: ID da empresa
            skip: Número de registros para pular
            limit: Número máximo de registros
            tipo: Filtrar por tipo
            status: Filtrar por status
            busca: Termo para busca
            
        Returns:
            Lista paginada de categorias
        """
        try:
            categorias, total = await self.repository.get_multi(
                empresa_id=empresa_id,
                skip=skip,
                limit=limit,
                tipo=tipo,
                status=status,
                busca=busca
            )
            
            return PaginatedResponse(
                items=categorias,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                pages=(total + limit - 1) // limit if limit > 0 else 1
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar categorias: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar categorias"
            ) 