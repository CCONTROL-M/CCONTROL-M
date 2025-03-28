"""Serviço para gerenciamento de fornecedores no sistema CCONTROL-M."""
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
import logging
from datetime import datetime

from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate, Fornecedor
from app.repositories.fornecedor_repository import FornecedorRepository
from app.database import db_async_session, get_async_session
from app.utils.validators import validar_cnpj, validar_email, validar_telefone, formatar_cnpj
from app.services.log_sistema_service import LogSistemaService
from app.schemas.log_sistema import LogSistemaCreate
from app.schemas.pagination import PaginatedResponse
from app.services.auditoria_service import AuditoriaService


# Configurar logger
logger = logging.getLogger(__name__)


class FornecedorService:
    """Serviço para gerenciamento de fornecedores."""
    
    def __init__(self, 
                 session: AsyncSession = Depends(get_async_session),
                 auditoria_service: AuditoriaService = Depends()):
        """Inicializar serviço com repositórios."""
        self.repository = FornecedorRepository(session)
        self.auditoria_service = auditoria_service
        self.logger = logger
    
    async def get_fornecedor(self, id_fornecedor: UUID, id_empresa: UUID) -> Fornecedor:
        """
        Buscar fornecedor pelo ID com validação de empresa.
        
        Args:
            id_fornecedor: ID do fornecedor
            id_empresa: ID da empresa
            
        Returns:
            Fornecedor encontrado
            
        Raises:
            HTTPException: Se o fornecedor não for encontrado
        """
        self.logger.info(f"Buscando fornecedor com ID: {id_fornecedor}")
        
        fornecedor = await self.repository.get_by_id(id_fornecedor, id_empresa)
        
        if not fornecedor:
            self.logger.warning(f"Fornecedor não encontrado: {id_fornecedor}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fornecedor não encontrado com ID: {id_fornecedor}"
            )
        
        return fornecedor
    
    async def listar_fornecedores(
        self,
        id_empresa: UUID,
        skip: int = 0,
        limit: int = 100,
        nome: Optional[str] = None,
        cnpj: Optional[str] = None,
        email: Optional[str] = None,
        telefone: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Tuple[List[Fornecedor], int]:
        """
        Listar fornecedores com filtros.
        
        Args:
            id_empresa: ID da empresa
            skip: Registros para pular
            limit: Limite de registros
            nome: Filtro por nome
            cnpj: Filtro por CNPJ
            email: Filtro por e-mail
            telefone: Filtro por telefone
            ativo: Filtro por status (ativo/inativo)
            
        Returns:
            Lista de fornecedores e contagem total
        """
        self.logger.info(f"Listando fornecedores para empresa {id_empresa}")
        
        # Construir filtros
        filters = {}
        if nome:
            filters["nome"] = nome
        if cnpj:
            filters["cnpj"] = cnpj
        if email:
            filters["email"] = email
        if telefone:
            filters["telefone"] = telefone
        if ativo is not None:
            filters["ativo"] = ativo
        
        try:
            fornecedores, total = await self.repository.list_with_filters(
                skip=skip,
                limit=limit,
                id_empresa=id_empresa,
                **filters
            )
            
            return fornecedores, total
        except Exception as e:
            self.logger.error(f"Erro ao listar fornecedores: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao listar fornecedores"
            )
    
    async def criar_fornecedor(self, fornecedor: FornecedorCreate, id_usuario: UUID) -> Fornecedor:
        """
        Criar novo fornecedor com validações.
        
        Args:
            fornecedor: Dados do fornecedor
            id_usuario: ID do usuário que está criando
            
        Returns:
            Fornecedor criado
            
        Raises:
            HTTPException: Se houver erro de validação
        """
        self.logger.info(f"Criando fornecedor: {fornecedor.nome}")
        
        try:
            # Validar CNPJ
            if fornecedor.cnpj:
                if not validar_cnpj(fornecedor.cnpj):
                    self.logger.warning(f"CNPJ inválido: {fornecedor.cnpj}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="CNPJ inválido"
                    )
                
                # Verificar se o CNPJ já está em uso
                existente = await self.repository.get_by_cnpj_empresa(
                    cnpj=fornecedor.cnpj, 
                    id_empresa=fornecedor.id_empresa
                )
                
                if existente:
                    self.logger.warning(f"CNPJ já cadastrado: {fornecedor.cnpj}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="CNPJ já cadastrado para outro fornecedor"
                    )
            
            # Validar e-mail, se fornecido
            if fornecedor.email and not validar_email(fornecedor.email):
                self.logger.warning(f"E-mail inválido: {fornecedor.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="E-mail inválido"
                )
            
            # Validar telefone, se fornecido
            if fornecedor.telefone and not validar_telefone(fornecedor.telefone):
                self.logger.warning(f"Telefone inválido: {fornecedor.telefone}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Telefone em formato inválido"
                )
            
            # Formatar documento se necessário
            if fornecedor.cnpj:
                fornecedor.cnpj = formatar_cnpj(fornecedor.cnpj)
            
            # Preparar dados para criação
            fornecedor_data = fornecedor.model_dump()
            
            # Adicionar metadados
            fornecedor_data.update({
                "id_fornecedor": uuid4(),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "ativo": True  # Por padrão, fornecedor é criado como ativo
            })
            
            # Criar fornecedor
            fornecedor_obj = await self.repository.create(fornecedor_data)
            
            # Registrar auditoria
            await self.auditoria_service.registrar_auditoria(
                usuario_id=id_usuario,
                empresa_id=fornecedor.id_empresa,
                acao="Criação de fornecedor",
                recurso="fornecedor",
                recurso_id=str(fornecedor_obj.id_fornecedor),
                dados_novos=fornecedor_data,
                ip_address="127.0.0.1",  # Idealmente deve vir do request
                detalhes=f"Criação do fornecedor {fornecedor.nome}"
            )
            
            return fornecedor_obj
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao criar fornecedor: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar fornecedor: {str(e)}"
            )
    
    async def atualizar_fornecedor(
        self, 
        id_fornecedor: UUID, 
        fornecedor: FornecedorUpdate, 
        id_empresa: UUID,
        id_usuario: UUID
    ) -> Fornecedor:
        """
        Atualizar fornecedor existente com validações.
        
        Args:
            id_fornecedor: ID do fornecedor
            fornecedor: Dados para atualização
            id_empresa: ID da empresa para validação
            id_usuario: ID do usuário que está atualizando
            
        Returns:
            Fornecedor atualizado
            
        Raises:
            HTTPException: Se houver erro de validação ou o fornecedor não for encontrado
        """
        self.logger.info(f"Atualizando fornecedor ID: {id_fornecedor}")
        
        try:
            # Verificar se o fornecedor existe
            await self.get_fornecedor(id_fornecedor, id_empresa)
            
            # Validar CNPJ, se fornecido
            if fornecedor.cnpj:
                if not validar_cnpj(fornecedor.cnpj):
                    self.logger.warning(f"CNPJ inválido: {fornecedor.cnpj}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="CNPJ inválido"
                    )
                
                # Verificar se o CNPJ já está em uso por outro fornecedor
                existente = await self.repository.get_by_cnpj_empresa(
                    cnpj=fornecedor.cnpj, 
                    id_empresa=id_empresa
                )
                
                if existente and existente.id_fornecedor != id_fornecedor:
                    self.logger.warning(f"CNPJ já cadastrado: {fornecedor.cnpj}")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="CNPJ já cadastrado para outro fornecedor"
                    )
            
            # Preparar dados para atualização
            fornecedor_dict = fornecedor.model_dump(exclude_unset=True)
            
            # Atualizar fornecedor
            fornecedor_atualizado = await self.repository.update(
                id_fornecedor=id_fornecedor,
                data=fornecedor_dict,
                id_empresa=id_empresa
            )
            
            if not fornecedor_atualizado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fornecedor não encontrado"
                )
            
            # Registrar log
            log = LogSistemaCreate(
                acao="atualizar",
                tabela="fornecedores",
                id_registro=str(id_fornecedor),
                id_usuario=id_usuario,
                id_empresa=id_empresa,
                detalhes=f"Fornecedor {fornecedor_atualizado.nome} atualizado"
            )
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="ATUALIZAR_FORNECEDOR",
                detalhes={
                    "id_fornecedor": str(id_fornecedor),
                    "alteracoes": fornecedor.model_dump(exclude_unset=True)
                },
                empresa_id=id_empresa
            )
            
            # Comitar alterações
            await self.repository.commit()
            
            return fornecedor_atualizado
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao atualizar fornecedor: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao atualizar fornecedor: {str(e)}"
            )
    
    async def remover_fornecedor(self, id_fornecedor: UUID, id_empresa: UUID, id_usuario: UUID) -> Dict[str, Any]:
        """
        Remover fornecedor pelo ID.
        
        Args:
            id_fornecedor: ID do fornecedor
            id_empresa: ID da empresa para validação
            id_usuario: ID do usuário que está removendo
            
        Returns:
            Mensagem de confirmação
            
        Raises:
            HTTPException: Se o fornecedor não for encontrado ou não puder ser removido
        """
        self.logger.info(f"Removendo fornecedor ID: {id_fornecedor}")
        
        try:
            # Verificar se o fornecedor existe
            fornecedor = await self.get_fornecedor(id_fornecedor, id_empresa)
            
            # Verificar se existem relações que impedem a remoção
            # Exemplo: pedidos, contas a pagar, etc.
            # TODO: Implementar verificações de relações
            
            # Remover fornecedor
            resultado = await self.repository.delete(id_fornecedor, id_empresa)
            if not resultado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fornecedor não encontrado"
                )
            
            # Registrar log
            log = LogSistemaCreate(
                acao="remover",
                tabela="fornecedores",
                id_registro=str(id_fornecedor),
                id_usuario=id_usuario,
                id_empresa=id_empresa,
                detalhes=f"Fornecedor {fornecedor.nome} removido"
            )
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="EXCLUIR_FORNECEDOR",
                detalhes={
                    "id_fornecedor": str(id_fornecedor),
                    "nome": fornecedor.nome,
                    "tipo": fornecedor.tipo,
                    "documento": fornecedor.documento
                },
                empresa_id=id_empresa
            )
            
            # Comitar alterações
            await self.repository.commit()
            
            return {"mensagem": "Fornecedor removido com sucesso"}
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao remover fornecedor: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover fornecedor: {str(e)}"
            )
            
    async def desativar_fornecedor(self, id_fornecedor: UUID, id_empresa: UUID, id_usuario: UUID) -> Fornecedor:
        """
        Desativar um fornecedor (alternar status para inativo).
        
        Args:
            id_fornecedor: ID do fornecedor
            id_empresa: ID da empresa para validação
            id_usuario: ID do usuário que está desativando
            
        Returns:
            Fornecedor desativado
            
        Raises:
            HTTPException: Se o fornecedor não for encontrado
        """
        self.logger.info(f"Desativando fornecedor ID: {id_fornecedor}")
        
        try:
            # Verificar se o fornecedor existe
            fornecedor = await self.get_fornecedor(id_fornecedor, id_empresa)
            
            # Se já estiver inativo, não precisa fazer nada
            if not fornecedor.ativo:
                return fornecedor
            
            # Atualizar status para inativo
            fornecedor_atualizado = await self.repository.update(
                id_fornecedor=id_fornecedor,
                data={"ativo": False},
                id_empresa=id_empresa
            )
            
            # Registrar log
            log = LogSistemaCreate(
                acao="desativar",
                tabela="fornecedores",
                id_registro=str(id_fornecedor),
                id_usuario=id_usuario,
                id_empresa=id_empresa,
                detalhes=f"Fornecedor {fornecedor.nome} desativado"
            )
            await self.auditoria_service.registrar_acao(
                usuario_id=id_usuario,
                acao="DESATIVAR_FORNECEDOR",
                detalhes={
                    "id_fornecedor": str(id_fornecedor),
                    "nome": fornecedor.nome,
                    "tipo": fornecedor.tipo,
                    "documento": fornecedor.documento
                },
                empresa_id=id_empresa
            )
            
            # Comitar alterações
            await self.repository.commit()
            
            return fornecedor_atualizado
        except HTTPException:
            await self.repository.rollback()
            raise
        except Exception as e:
            await self.repository.rollback()
            self.logger.error(f"Erro ao desativar fornecedor: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao desativar fornecedor: {str(e)}"
            ) 