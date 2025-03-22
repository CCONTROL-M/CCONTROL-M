"""Script para testar se os schemas criados funcionam corretamente de forma isolada."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, UUID4
from typing import Optional, List, Dict, Any, Union


# Simulação de modelos base para teste
class PaginatedResponse(BaseModel):
    total: int
    items: List[Any]


# Categoria
class CategoriaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    cor: Optional[str] = None
    tipo: str
    nivel: Optional[int] = 1


class CategoriaCreate(CategoriaBase):
    id_empresa: UUID4


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    cor: Optional[str] = None
    tipo: Optional[str] = None
    ativa: Optional[bool] = None
    nivel: Optional[int] = None
    id_categoria_pai: Optional[UUID4] = None


class Categoria(CategoriaBase):
    id_categoria: UUID4
    id_empresa: UUID4
    ativa: bool = True
    created_at: datetime
    subcategorias: List["Categoria"] = []

    class Config:
        from_attributes = True


# Centro de Custo
class CentroCustoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None


class CentroCustoCreate(CentroCustoBase):
    id_empresa: UUID4


class CentroCustoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None


class CentroCusto(CentroCustoBase):
    id_centro: UUID4
    id_empresa: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


# Cliente
class ClienteBase(BaseModel):
    nome: str
    documento: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None


class ClienteCreate(ClienteBase):
    id_empresa: UUID4


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    documento: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None


class Cliente(ClienteBase):
    id_cliente: UUID4
    id_empresa: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


# Fornecedor
class FornecedorBase(BaseModel):
    nome: str
    documento: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None


class FornecedorCreate(FornecedorBase):
    id_empresa: UUID4


class FornecedorUpdate(BaseModel):
    nome: Optional[str] = None
    documento: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None


class Fornecedor(FornecedorBase):
    id_fornecedor: UUID4
    id_empresa: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


# Log Sistema
class LogSistemaBase(BaseModel):
    acao: str
    descricao: str
    dados: Optional[Dict[str, Any]] = None


class LogSistemaCreate(LogSistemaBase):
    id_empresa: Optional[UUID4] = None
    id_usuario: Optional[UUID4] = None


class LogSistemaInDB(LogSistemaBase):
    id_log: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LogSistema(LogSistemaInDB):
    pass


def test_categoria_schema():
    """Testa o schema de categoria."""
    # Dados para criação
    id_empresa = uuid.uuid4()
    id_categoria = uuid.uuid4()
    
    # Criar dados de categoria
    categoria_create = CategoriaCreate(
        nome="Despesas Gerais",
        descricao="Despesas gerais da empresa",
        cor="#FF0000",
        tipo="DESPESA",
        id_empresa=id_empresa
    )
    
    # Verificar se os dados são válidos
    print(f"CategoriaCreate válido: {categoria_create.model_dump()}")
    
    # Criar objeto de categoria completo
    categoria = Categoria(
        id_categoria=id_categoria,
        id_empresa=id_empresa,
        nome="Despesas Gerais",
        descricao="Despesas gerais da empresa",
        cor="#FF0000",
        tipo="DESPESA",
        ativa=True,
        nivel=1,
        created_at=datetime.now(),
        subcategorias=[]
    )
    
    # Verificar se os dados são válidos
    print(f"Categoria válida: {categoria.model_dump()}")
    
    # Testar atualização parcial
    categoria_update = CategoriaUpdate(
        nome="Despesas Operacionais",
        ativa=False
    )
    
    # Verificar se os dados são válidos
    print(f"CategoriaUpdate válido: {categoria_update.model_dump()}")


def test_centro_custo_schema():
    """Testa o schema de centro de custo."""
    # Dados para criação
    id_empresa = uuid.uuid4()
    id_centro = uuid.uuid4()
    
    # Criar dados de centro de custo
    centro_custo_create = CentroCustoCreate(
        nome="Departamento de TI",
        descricao="Centro de custo para TI",
        id_empresa=id_empresa
    )
    
    # Verificar se os dados são válidos
    print(f"CentroCustoCreate válido: {centro_custo_create.model_dump()}")
    
    # Criar objeto de centro de custo completo
    centro_custo = CentroCusto(
        id_centro=id_centro,
        id_empresa=id_empresa,
        nome="Departamento de TI",
        descricao="Centro de custo para TI",
        created_at=datetime.now()
    )
    
    # Verificar se os dados são válidos
    print(f"CentroCusto válido: {centro_custo.model_dump()}")


def test_cliente_schema():
    """Testa o schema de cliente."""
    # Dados para criação
    id_empresa = uuid.uuid4()
    id_cliente = uuid.uuid4()
    
    # Criar dados de cliente
    cliente_create = ClienteCreate(
        nome="João Silva",
        documento="123.456.789-00",
        telefone="(11) 99999-9999",
        email="joao@exemplo.com",
        id_empresa=id_empresa
    )
    
    # Verificar se os dados são válidos
    print(f"ClienteCreate válido: {cliente_create.model_dump()}")
    
    # Criar objeto de cliente completo
    cliente = Cliente(
        id_cliente=id_cliente,
        id_empresa=id_empresa,
        nome="João Silva",
        documento="123.456.789-00",
        telefone="(11) 99999-9999",
        email="joao@exemplo.com",
        created_at=datetime.now()
    )
    
    # Verificar se os dados são válidos
    print(f"Cliente válido: {cliente.model_dump()}")


def test_fornecedor_schema():
    """Testa o schema de fornecedor."""
    # Dados para criação
    id_empresa = uuid.uuid4()
    id_fornecedor = uuid.uuid4()
    
    # Criar dados de fornecedor
    fornecedor_create = FornecedorCreate(
        nome="Empresa ABC",
        documento="12.345.678/0001-90",
        telefone="(11) 3333-3333",
        email="contato@empresaabc.com",
        observacoes="Fornecedor principal",
        id_empresa=id_empresa
    )
    
    # Verificar se os dados são válidos
    print(f"FornecedorCreate válido: {fornecedor_create.model_dump()}")
    
    # Criar objeto de fornecedor completo
    fornecedor = Fornecedor(
        id_fornecedor=id_fornecedor,
        id_empresa=id_empresa,
        nome="Empresa ABC",
        documento="12.345.678/0001-90",
        telefone="(11) 3333-3333",
        email="contato@empresaabc.com",
        observacoes="Fornecedor principal",
        created_at=datetime.now()
    )
    
    # Verificar se os dados são válidos
    print(f"Fornecedor válido: {fornecedor.model_dump()}")


def test_log_sistema_schema():
    """Testa o schema de log do sistema."""
    # Dados para criação
    id_empresa = uuid.uuid4()
    id_usuario = uuid.uuid4()
    id_log = uuid.uuid4()
    
    # Criar dados de log
    log_create = LogSistemaCreate(
        acao="LOGIN",
        descricao="Usuário realizou login no sistema",
        dados={"ip": "192.168.0.1", "browser": "Chrome"},
        id_empresa=id_empresa,
        id_usuario=id_usuario
    )
    
    # Verificar se os dados são válidos
    print(f"LogSistemaCreate válido: {log_create.model_dump()}")
    
    # Criar objeto de log completo
    log = LogSistema(
        id_log=id_log,
        acao="LOGIN",
        descricao="Usuário realizou login no sistema",
        dados={"ip": "192.168.0.1", "browser": "Chrome"},
        created_at=datetime.now()
    )
    
    # Verificar se os dados são válidos
    print(f"LogSistema válido: {log.model_dump()}")


if __name__ == "__main__":
    print("Testando schemas criados...")
    test_categoria_schema()
    test_centro_custo_schema()
    test_cliente_schema()
    test_fornecedor_schema()
    test_log_sistema_schema()
    print("Todos os testes concluídos com sucesso!") 