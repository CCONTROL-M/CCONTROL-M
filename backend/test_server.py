"""
Servidor de teste para rotas de lançamentos financeiros.
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID, uuid4
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="CCONTROL-M Teste",
    description="Servidor de teste para rotas de lançamentos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definição simplificada de Lancamento para teste
class Lancamento:
    def __init__(
        self,
        id: UUID,
        descricao: str,
        valor: float,
        data_lancamento: str,
        data_pagamento: Optional[str],
        tipo: str,
        status: str,
        id_categoria: UUID,
        id_empresa: UUID
    ):
        self.id = id
        self.descricao = descricao
        self.valor = valor
        self.data_lancamento = data_lancamento
        self.data_pagamento = data_pagamento
        self.tipo = tipo
        self.status = status
        self.id_categoria = id_categoria
        self.id_empresa = id_empresa
    
    def dict(self):
        return {
            "id": str(self.id),
            "descricao": self.descricao,
            "valor": self.valor,
            "data_lancamento": self.data_lancamento,
            "data_pagamento": self.data_pagamento,
            "tipo": self.tipo,
            "status": self.status,
            "id_categoria": str(self.id_categoria),
            "id_empresa": str(self.id_empresa)
        }

# Função para paginar resultados
def paginate(items, total, page, page_size):
    return {
        "items": [item.dict() for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }

@app.get("/health")
async def health_check():
    """Rota para verificação de saúde da API de teste."""
    return {"status": "ok", "version": "1.0.0"}

@app.get("/api/v1/lancamentos")
async def listar_lancamentos(
    id_empresa: UUID = Query(..., description="ID da empresa", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (RECEITA, DESPESA)", example="DESPESA"),
    status: Optional[str] = Query(None, description="Filtrar por status (PENDENTE, PAGO, CANCELADO)", example="PENDENTE"),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
):
    """
    Rota de teste para lançamentos financeiros.
    """
    # Dados de teste
    lancamentos = [
        Lancamento(
            id=uuid4(),
            descricao=f"Lançamento de teste {i}",
            valor=100.0 * i,
            data_lancamento=f"2023-{i:02d}-01",
            data_pagamento=f"2023-{i:02d}-10" if i % 3 != 0 else None,
            tipo="RECEITA" if i % 2 == 0 else "DESPESA",
            status="PENDENTE" if i % 3 == 0 else ("PAGO" if i % 3 == 1 else "CANCELADO"),
            id_categoria=UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            id_empresa=id_empresa
        )
        for i in range(1, 21)  # Criar 20 lançamentos de teste
    ]
    
    # Filtrar resultados conforme parâmetros
    if tipo:
        lancamentos = [l for l in lancamentos if l.tipo == tipo]
    
    if status:
        lancamentos = [l for l in lancamentos if l.status == status]
    
    # Simular paginação
    total = len(lancamentos)
    
    # Calcular índices de início e fim para a página atual
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)
    
    # Obter itens da página atual
    page_items = lancamentos[start_idx:end_idx]
    
    # Retornar resposta paginada
    return paginate(page_items, total, page, page_size)

if __name__ == "__main__":
    print("Iniciando servidor de teste em http://localhost:8000")
    print("Rota de lançamentos disponível em: http://localhost:8000/api/v1/lancamentos?id_empresa=3fa85f64-5717-4562-b3fc-2c963f66afa6")
    uvicorn.run(app, host="0.0.0.0", port=8000) 