"""Módulo contendo a classe base para todos os serviços do sistema."""
import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel

from app.repositories.base_repository import BaseRepository

# Tipos genéricos para modelos
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Classe base para implementação de serviços com operações comuns.
    
    Argumentos:
        repository: Instância do repositório para acesso aos dados
    """

    def __init__(self, repository: BaseRepository):
        """
        Inicializa o serviço com um repositório.
        
        Args:
            repository: O repositório que será utilizado para operações de dados
        """
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def get_multi(
        self, 
        id_empresa: int,
        skip: int = 0, 
        limit: int = 100, 
        busca: Optional[str] = None,
        ordenar_por: Optional[str] = None,
        ordem: Optional[str] = "asc",
        **filters
    ) -> List[ModelType]:
        """
        Obtém múltiplos registros aplicando filtros, busca e ordenação.
        
        Args:
            id_empresa: ID da empresa para filtrar registros
            skip: Quantidade de registros para pular
            limit: Quantidade máxima de registros a retornar
            busca: Termo para busca nos campos do modelo
            ordenar_por: Campo pelo qual ordenar os resultados
            ordem: Direção da ordenação (asc/desc)
            **filters: Filtros adicionais a serem aplicados
            
        Returns:
            Lista de registros encontrados
        """
        self.logger.info(
            f"Buscando registros com filtros: id_empresa={id_empresa}, "
            f"skip={skip}, limit={limit}, busca={busca}, ordenar_por={ordenar_por}, "
            f"ordem={ordem}, filtros_adicionais={filters}"
        )
        
        # Validar ordenação
        if ordenar_por and ordem not in ["asc", "desc"]:
            self.logger.warning(f"Ordem inválida: {ordem}. Usando 'asc' como padrão.")
            ordem = "asc"
            
        # Aplicar filtro de empresa e outros filtros
        all_filters = {"id_empresa": id_empresa, **filters}
        
        return self.repository.get_multi(
            skip=skip, 
            limit=limit, 
            busca=busca,
            ordenar_por=ordenar_por,
            ordem=ordem,
            **all_filters
        )
    
    def get_by_id(self, id: int, id_empresa: int) -> ModelType:
        """
        Obtém um registro pelo ID, garantindo que pertence à empresa.
        
        Args:
            id: ID do registro a ser obtido
            id_empresa: ID da empresa para validar pertencimento
            
        Returns:
            Registro encontrado
            
        Raises:
            HTTPException: Se o registro não for encontrado
        """
        self.logger.info(f"Buscando registro com ID={id} para empresa {id_empresa}")
        
        obj = self.repository.get_by_id(id, id_empresa=id_empresa)
        if not obj:
            self.logger.warning(f"Registro com ID={id} não encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro não encontrado"
            )
        
        return obj
    
    def create(self, obj_in: CreateSchemaType, id_empresa: int) -> ModelType:
        """
        Cria um novo registro.
        
        Args:
            obj_in: Dados para criação do registro
            id_empresa: ID da empresa a qual o registro pertencerá
            
        Returns:
            Registro criado
        """
        self.logger.info(f"Criando novo registro para empresa {id_empresa}")
        
        # Converter para dict e adicionar id_empresa
        obj_data = obj_in.dict()
        obj_data["id_empresa"] = id_empresa
        
        return self.repository.create(obj_data)
    
    def update(self, id: int, obj_in: UpdateSchemaType, id_empresa: int) -> ModelType:
        """
        Atualiza um registro existente.
        
        Args:
            id: ID do registro a ser atualizado
            obj_in: Dados para atualização
            id_empresa: ID da empresa para validação
            
        Returns:
            Registro atualizado
            
        Raises:
            HTTPException: Se o registro não for encontrado
        """
        self.logger.info(f"Atualizando registro ID={id} para empresa {id_empresa}")
        
        # Verificar se registro existe
        obj = self.get_by_id(id, id_empresa)
        
        # Converter para dict 
        update_data = obj_in.dict(exclude_unset=True)
        
        return self.repository.update(id, update_data)
    
    def delete(self, id: int, id_empresa: int) -> ModelType:
        """
        Remove um registro.
        
        Args:
            id: ID do registro a ser removido
            id_empresa: ID da empresa para validação
            
        Returns:
            Registro removido
            
        Raises:
            HTTPException: Se o registro não for encontrado
        """
        self.logger.info(f"Removendo registro ID={id} para empresa {id_empresa}")
        
        # Verificar se registro existe
        obj = self.get_by_id(id, id_empresa)
        
        return self.repository.delete(id) 