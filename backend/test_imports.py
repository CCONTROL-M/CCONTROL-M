"""Script para testar importações."""

def test_lancamento_simples():
    try:
        from app.schemas.lancamento_simples import (
            Lancamento,
            LancamentoCreate,
            LancamentoUpdate,
            LancamentoWithDetalhes,
            PaginatedResponse,
            RelatorioFinanceiro
        )
        print("Módulo lancamento_simples importado com sucesso")
        print(f"Lancamento: {Lancamento.__name__}")
        print(f"LancamentoCreate: {LancamentoCreate.__name__}")
        return True
    except Exception as e:
        print(f"Erro ao importar lancamento_simples: {str(e)}")
        return False

def test_pagination():
    try:
        from app.utils.pagination import paginate
        print("Módulo pagination importado com sucesso")
        print(f"paginate: {paginate.__name__}")
        return True
    except Exception as e:
        print(f"Erro ao importar pagination: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testando importações dos módulos...")
    test_lancamento_simples()
    test_pagination()
    print("Testes concluídos") 