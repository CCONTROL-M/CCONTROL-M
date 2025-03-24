#!/usr/bin/env python
"""
Script para geração de dados de teste para o sistema CCONTROL-M.

Este script popula o banco de dados com dados realistas para testes, incluindo:
- Empresas
- Usuários
- Clientes
- Fornecedores
- Categorias
- Produtos
- Contas bancárias
- Formas de pagamento
- Vendas
- Lançamentos financeiros

O objetivo é criar um ambiente de teste com dados suficientes para demonstrar
todas as funcionalidades do sistema, mas sem sobrecarregar o banco de dados.

Uso:
    python -m app.scripts.seed_data

Ambiente:
    - Configurado para funcionar com SQLite e PostgreSQL
    - Usa SQLAlchemy para manipulação do banco de dados
    - Funciona de forma síncrona para evitar problemas com greenlets
"""

import os
import sys
import random
import string
import uuid
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

# Configurar o path para importação dos módulos do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Importar models e dependências do projeto
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.fornecedor import Fornecedor
from app.models.categoria import Categoria
from app.models.centro_custo import CentroCusto
from app.models.conta_bancaria import ContaBancaria
from app.models.forma_pagamento import FormaPagamento
from app.models.produto import Produto
from app.models.venda import Venda
from app.models.parcela import Parcela, ParcelaVenda
from app.models.lancamento import Lancamento
from app.database import create_all_tables, SessionLocal

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações gerais
QUANTIDADE_EMPRESAS = 2
QUANTIDADE_CLIENTES_POR_EMPRESA = 20
QUANTIDADE_FORNECEDORES_POR_EMPRESA = 15
QUANTIDADE_PRODUTOS_POR_EMPRESA = 30
QUANTIDADE_VENDAS_POR_EMPRESA = 50
QUANTIDADE_LANCAMENTOS_POR_EMPRESA = 100
DATA_INICIO = date(2023, 1, 1)
DATA_FIM = date(2023, 12, 31)
HOJE = date.today()

# Listas de dados para criação aleatória
NOMES_EMPRESAS = [
    "TechSolutions Ltda", "Comércio ABC", "Distribuidora FastDelivery", 
    "Indústria Nacional SA", "Serviços Especializados ME"
]

NOMES_CLIENTES = [
    "João Silva", "Maria Santos", "Carlos Ferreira", "Ana Oliveira", 
    "Pedro Costa", "Márcia Lima", "Antônio Souza", "Juliana Rodrigues",
    "Fábio Almeida", "Cristina Pereira", "Ricardo Gomes", "Patrícia Martins",
    "Lucas Araújo", "Fernanda Carvalho", "Roberto Vieira", "Aline Castro",
    "Márcio Ribeiro", "Cláudia Barbosa", "Eduardo Cardoso", "Beatriz Correia"
]

NOMES_EMPRESAS_CLIENTES = [
    "SupermercadosBom", "Lojas Econômicas", "Farmácia Saúde Total", 
    "Auto Peças Express", "Restaurante Sabor Caseiro", "Padaria Pão Quente", 
    "Materiais de Construção Forte", "Eletrônicos Digitais", 
    "Livraria Cultura", "Roupas Fashion", "Calçados Conforto", 
    "Móveis Decoração", "Papelaria Escolar", "Cosméticos Beleza", 
    "Academia Fitness", "Pet Shop Amigo Fiel", "Joalheria Brilhante", 
    "Ótica Visão Clara", "Concessionária Veículos", "Hotel Estrelas"
]

NOMES_FORNECEDORES = [
    "Distribuidora Nacional", "Importadora Global", "Fábrica Industrial", 
    "Atacado Express", "Serviços Profissionais", "Insumos Básicos",
    "Equipamentos Técnicos", "Material de Escritório", "Tecnologia Avançada", 
    "Logística Integrada", "Alimentos Premium", "Embalagens Práticas",
    "Produtos Químicos", "Papéis Especiais", "Uniformes Corporativos"
]

TIPOS_CONTAS = ["Corrente", "Poupança", "Investimento", "Aplicação"]
BANCOS = ["Banco do Brasil", "Itaú", "Bradesco", "Santander", "Caixa Econômica", "Nubank", "Inter"]

FORMAS_PAGAMENTO = [
    "Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito", 
    "Boleto Bancário", "Transferência", "Cheque"
]

TIPOS_CATEGORIAS_RECEITA = [
    "Vendas de Produtos", "Prestação de Serviços", "Comissões", 
    "Juros Recebidos", "Aluguel", "Royalties", "Outras Receitas"
]

TIPOS_CATEGORIAS_DESPESA = [
    "Aluguel", "Salários", "Fornecedores", "Energia Elétrica", 
    "Água", "Internet/Telefone", "Material de Escritório", 
    "Marketing", "Impostos", "Serviços Terceirizados", 
    "Manutenção", "Combustível", "Seguros", "Despesas Bancárias"
]

CENTROS_CUSTO = [
    "Administrativo", "Comercial", "Financeiro", "Marketing", 
    "RH", "TI", "Logística", "Produção", "Vendas", "Compras"
]

PRODUTOS = [
    "Notebook", "Smartphone", "Monitor", "Teclado", "Mouse", "Impressora", 
    "Tablet", "Smart TV", "Fone de Ouvido", "Câmera", "HD Externo", "Pendrive",
    "Roteador", "Switch", "Cabo HDMI", "Adaptador USB", "Carregador", "Bateria",
    "Caixa de Som", "Projetor", "Mousepad", "Webcam", "Microfone", "Headset"
]

def data_aleatoria(inicio: date, fim: date) -> date:
    """Gera uma data aleatória entre duas datas."""
    dias = (fim - inicio).days
    return inicio + timedelta(days=random.randint(0, dias))

def criar_empresas(session: Session) -> List[Empresa]:
    """Cria empresas de teste no banco de dados."""
    empresas = []
    
    for i in range(QUANTIDADE_EMPRESAS):
        nome = NOMES_EMPRESAS[i % len(NOMES_EMPRESAS)]
        cnpj = f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/{random.randint(1000, 9999)}-{random.randint(10, 99)}"
        
        empresa = Empresa(
            razao_social=f"{nome} {i+1}",
            nome_fantasia=f"{nome.split(' ')[0]} {i+1}",
            cnpj=cnpj,
            email=f"contato@{nome.lower().replace(' ', '')}{i+1}.com.br",
            telefone=f"({random.randint(11, 99)}) {random.randint(10000, 99999)}-{random.randint(1000, 9999)}",
            endereco=f"Rua Exemplo, {random.randint(1, 999)}",
            cidade=random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre"]),
            estado=random.choice(["SP", "RJ", "MG", "PR", "RS"])
        )
        
        session.add(empresa)
        empresas.append(empresa)
    
    session.commit()
    print(f"✓ {len(empresas)} empresas criadas")
    return empresas

def criar_usuarios(session: Session, empresas: List[Empresa]) -> List[Usuario]:
    """Cria usuários de teste para as empresas."""
    usuarios = []
    
    for empresa in empresas:
        # Criar um administrador
        admin = Usuario(
            id_empresa=empresa.id_empresa,
            nome=f"Admin {empresa.nome_fantasia}",
            email=f"admin@{empresa.email.split('@')[1]}",
            hashed_password="$2b$12$A9GbfPgQJEmQw2SNoL5K7uY1MSVa8MDSD0S4D9jDzQHjicZKiTBQ2",  # senha: admin123
            is_admin=True,
            is_active=True
        )
        
        # Criar um usuário comum
        usuario = Usuario(
            id_empresa=empresa.id_empresa,
            nome=f"Usuário {empresa.nome_fantasia}",
            email=f"usuario@{empresa.email.split('@')[1]}",
            hashed_password="$2b$12$A9GbfPgQJEmQw2SNoL5K7uY1MSVa8MDSD0S4D9jDzQHjicZKiTBQ2",  # senha: admin123
            is_admin=False,
            is_active=True
        )
        
        session.add(admin)
        session.add(usuario)
        usuarios.extend([admin, usuario])
    
    session.commit()
    print(f"✓ {len(usuarios)} usuários criados")
    return usuarios

def criar_clientes(session: Session, empresas: List[Empresa]) -> List[Cliente]:
    """Cria clientes de teste para as empresas."""
    clientes = []
    
    for empresa in empresas:
        for i in range(QUANTIDADE_CLIENTES_POR_EMPRESA):
            # Alternar entre pessoa física e jurídica
            pessoa_juridica = random.choice([True, False])
            
            if pessoa_juridica:
                nome = NOMES_EMPRESAS_CLIENTES[i % len(NOMES_EMPRESAS_CLIENTES)]
                razao_social = f"{nome} {uuid.uuid4().hex[:4]}"
                nome_fantasia = nome
                cnpj = f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/{random.randint(1000, 9999)}-{random.randint(10, 99)}"
                cpf = None
            else:
                nome = NOMES_CLIENTES[i % len(NOMES_CLIENTES)]
                razao_social = None
                nome_fantasia = None
                cnpj = None
                cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
            
            cliente = Cliente(
                id_empresa=empresa.id_empresa,
                nome=nome,
                pessoa_juridica=pessoa_juridica,
                razao_social=razao_social,
                nome_fantasia=nome_fantasia,
                cpf=cpf,
                cnpj=cnpj,
                email=f"contato@{nome.lower().replace(' ', '')}.com.br" if pessoa_juridica else f"{nome.lower().replace(' ', '.')}{random.randint(1, 999)}@email.com",
                telefone=f"({random.randint(11, 99)}) {random.randint(10000, 99999)}-{random.randint(1000, 9999)}",
                endereco=f"Rua {random.choice(['das Flores', 'dos Pinheiros', 'Sete de Setembro', 'Augusta', 'Paulista'])}, {random.randint(1, 999)}",
                cidade=random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre", "Salvador", "Fortaleza"]),
                estado=random.choice(["SP", "RJ", "MG", "PR", "RS", "BA", "CE"]),
                observacoes="Cliente de teste" if random.random() < 0.3 else None
            )
            
            session.add(cliente)
            clientes.append(cliente)
    
    session.commit()
    print(f"✓ {len(clientes)} clientes criados")
    return clientes

def criar_fornecedores(session: Session, empresas: List[Empresa]) -> List[Fornecedor]:
    """Cria fornecedores de teste para as empresas."""
    fornecedores = []
    
    for empresa in empresas:
        for i in range(QUANTIDADE_FORNECEDORES_POR_EMPRESA):
            nome = NOMES_FORNECEDORES[i % len(NOMES_FORNECEDORES)]
            
            fornecedor = Fornecedor(
                id_empresa=empresa.id_empresa,
                razao_social=f"{nome} {uuid.uuid4().hex[:4]}",
                nome_fantasia=f"{nome.split(' ')[0]}",
                cnpj=f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/{random.randint(1000, 9999)}-{random.randint(10, 99)}",
                email=f"contato@{nome.lower().replace(' ', '')}.com.br",
                telefone=f"({random.randint(11, 99)}) {random.randint(10000, 99999)}-{random.randint(1000, 9999)}",
                endereco=f"Av. {random.choice(['Brasil', 'Paulista', 'Atlântica', 'Getúlio Vargas', 'Amazonas'])}, {random.randint(1, 9999)}",
                cidade=random.choice(["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre", "Recife", "Brasília"]),
                estado=random.choice(["SP", "RJ", "MG", "PR", "RS", "PE", "DF"]),
                contato=f"{random.choice(['Ana', 'João', 'Pedro', 'Maria', 'Carlos', 'Mariana', 'Rafael'])} {random.choice(['Silva', 'Oliveira', 'Santos', 'Costa', 'Pereira'])}",
                observacoes="Fornecedor de teste" if random.random() < 0.3 else None
            )
            
            session.add(fornecedor)
            fornecedores.append(fornecedor)
    
    session.commit()
    print(f"✓ {len(fornecedores)} fornecedores criados")
    return fornecedores

def criar_categorias(session: Session, empresas: List[Empresa]) -> Dict[int, Dict[str, List[Categoria]]]:
    """Cria categorias para receitas e despesas."""
    categorias_por_empresa = {}
    
    for empresa in empresas:
        categorias_receita = []
        categorias_despesa = []
        
        # Categorias de Receita
        for tipo in TIPOS_CATEGORIAS_RECEITA:
            categoria = Categoria(
                id_empresa=empresa.id_empresa,
                nome=tipo,
                tipo="RECEITA",
                descricao=f"Categoria para {tipo.lower()}"
            )
            session.add(categoria)
            categorias_receita.append(categoria)
        
        # Categorias de Despesa
        for tipo in TIPOS_CATEGORIAS_DESPESA:
            categoria = Categoria(
                id_empresa=empresa.id_empresa,
                nome=tipo,
                tipo="DESPESA",
                descricao=f"Categoria para {tipo.lower()}"
            )
            session.add(categoria)
            categorias_despesa.append(categoria)
        
        categorias_por_empresa[empresa.id_empresa] = {
            "receita": categorias_receita,
            "despesa": categorias_despesa
        }
    
    session.commit()
    total_categorias = sum(len(cats["receita"]) + len(cats["despesa"]) for cats in categorias_por_empresa.values())
    print(f"✓ {total_categorias} categorias criadas")
    return categorias_por_empresa

def criar_centros_custo(session: Session, empresas: List[Empresa]) -> Dict[int, List[CentroCusto]]:
    """Cria centros de custo para as empresas."""
    centros_por_empresa = {}
    
    for empresa in empresas:
        centros = []
        
        for nome in CENTROS_CUSTO:
            centro = CentroCusto(
                id_empresa=empresa.id_empresa,
                nome=nome,
                descricao=f"Centro de custo para {nome.lower()}"
            )
            session.add(centro)
            centros.append(centro)
        
        centros_por_empresa[empresa.id_empresa] = centros
    
    session.commit()
    total_centros = sum(len(centros) for centros in centros_por_empresa.values())
    print(f"✓ {total_centros} centros de custo criados")
    return centros_por_empresa

def criar_contas_bancarias(session: Session, empresas: List[Empresa]) -> Dict[int, List[ContaBancaria]]:
    """Cria contas bancárias para as empresas."""
    contas_por_empresa = {}
    
    for empresa in empresas:
        contas = []
        
        # Cada empresa terá entre 3 e 5 contas bancárias
        for _ in range(random.randint(3, 5)):
            banco = random.choice(BANCOS)
            tipo = random.choice(TIPOS_CONTAS)
            agencia = f"{random.randint(1000, 9999)}"
            conta = f"{random.randint(10000, 99999)}-{random.randint(0, 9)}"
            saldo_inicial = Decimal(str(random.uniform(1000, 50000))).quantize(Decimal('0.01'))
            
            conta_bancaria = ContaBancaria(
                id_empresa=empresa.id_empresa,
                banco=banco,
                tipo=tipo,
                agencia=agencia,
                conta=conta,
                descricao=f"{banco} - {tipo}",
                saldo_inicial=saldo_inicial,
                data_saldo_inicial=DATA_INICIO
            )
            
            session.add(conta_bancaria)
            contas.append(conta_bancaria)
        
        contas_por_empresa[empresa.id_empresa] = contas
    
    session.commit()
    total_contas = sum(len(contas) for contas in contas_por_empresa.values())
    print(f"✓ {total_contas} contas bancárias criadas")
    return contas_por_empresa

def criar_formas_pagamento(session: Session, empresas: List[Empresa], contas_bancarias: Dict[int, List[ContaBancaria]]) -> Dict[int, List[FormaPagamento]]:
    """Cria formas de pagamento para as empresas."""
    formas_por_empresa = {}
    
    for empresa in empresas:
        formas = []
        
        # Formas de pagamento padrão sem vinculação com conta bancária
        for nome in FORMAS_PAGAMENTO[:3]:  # Dinheiro, PIX, Cartão de Crédito
            forma = FormaPagamento(
                id_empresa=empresa.id_empresa,
                nome=nome,
                id_conta_bancaria=None,
                prazo_compensacao=0 if nome in ["Dinheiro", "PIX"] else 30,
                taxa_percentual=Decimal('0') if nome in ["Dinheiro", "PIX"] else Decimal('2.5'),
                taxa_fixa=Decimal('0')
            )
            session.add(forma)
            formas.append(forma)
        
        # Formas de pagamento vinculadas às contas bancárias
        contas = contas_bancarias[empresa.id_empresa]
        for i, conta in enumerate(contas):
            # Boleto para cada conta
            forma_boleto = FormaPagamento(
                id_empresa=empresa.id_empresa,
                nome=f"Boleto {conta.banco}",
                id_conta_bancaria=conta.id_conta_bancaria,
                prazo_compensacao=2,
                taxa_percentual=Decimal('0'),
                taxa_fixa=Decimal('2.95')
            )
            session.add(forma_boleto)
            formas.append(forma_boleto)
            
            # Transferência para cada conta
            forma_transferencia = FormaPagamento(
                id_empresa=empresa.id_empresa,
                nome=f"Transferência {conta.banco}",
                id_conta_bancaria=conta.id_conta_bancaria,
                prazo_compensacao=0,
                taxa_percentual=Decimal('0'),
                taxa_fixa=Decimal('0')
            )
            session.add(forma_transferencia)
            formas.append(forma_transferencia)
        
        formas_por_empresa[empresa.id_empresa] = formas
    
    session.commit()
    total_formas = sum(len(formas) for formas in formas_por_empresa.values())
    print(f"✓ {total_formas} formas de pagamento criadas")
    return formas_por_empresa

def criar_produtos(session: Session, empresas: List[Empresa]) -> Dict[int, List[Produto]]:
    """Cria produtos para as empresas."""
    produtos_por_empresa = {}
    
    for empresa in empresas:
        produtos_empresa = []
        
        for i in range(QUANTIDADE_PRODUTOS_POR_EMPRESA):
            nome_produto = PRODUTOS[i % len(PRODUTOS)]
            codigo = f"PROD-{i+1:04d}"
            preco_custo = Decimal(str(random.uniform(50, 1000))).quantize(Decimal('0.01'))
            preco_venda = preco_custo * Decimal(str(random.uniform(1.3, 2.5))).quantize(Decimal('0.01'))
            
            produto = Produto(
                id_empresa=empresa.id_empresa,
                nome=f"{nome_produto} {random.choice(['Pro', 'Premium', 'Basic', 'Ultra', 'Max', ''])}",
                codigo=codigo,
                descricao=f"Descrição detalhada do {nome_produto.lower()}",
                preco_custo=preco_custo,
                preco_venda=preco_venda,
                estoque_atual=random.randint(5, 100),
                estoque_minimo=random.randint(1, 10),
                unidade=random.choice(["UN", "KG", "CX", "PC"])
            )
            
            session.add(produto)
            produtos_empresa.append(produto)
        
        produtos_por_empresa[empresa.id_empresa] = produtos_empresa
    
    session.commit()
    total_produtos = sum(len(produtos) for produtos in produtos_por_empresa.values())
    print(f"✓ {total_produtos} produtos criados")
    return produtos_por_empresa

def criar_vendas_com_parcelas(
    session: Session, 
    empresas: List[Empresa], 
    clientes: List[Cliente], 
    produtos: Dict[int, List[Produto]], 
    formas_pagamento: Dict[int, List[FormaPagamento]]
) -> Tuple[List[Venda], List[ParcelaVenda]]:
    """Cria vendas e suas parcelas para as empresas."""
    todas_vendas = []
    todas_parcelas = []
    
    # Agrupar clientes por empresa
    clientes_por_empresa = {}
    for cliente in clientes:
        if cliente.id_empresa not in clientes_por_empresa:
            clientes_por_empresa[cliente.id_empresa] = []
        clientes_por_empresa[cliente.id_empresa].append(cliente)
    
    for empresa in empresas:
        clientes_empresa = clientes_por_empresa.get(empresa.id_empresa, [])
        produtos_empresa = produtos.get(empresa.id_empresa, [])
        formas_empresa = formas_pagamento.get(empresa.id_empresa, [])
        
        if not clientes_empresa or not produtos_empresa or not formas_empresa:
            continue
        
        # Criar vendas para a empresa
        for _ in range(QUANTIDADE_VENDAS_POR_EMPRESA):
            # Selecionar dados aleatórios para a venda
            cliente = random.choice(clientes_empresa)
            data_venda = data_aleatoria(DATA_INICIO, DATA_FIM)
            
            # Selecionar produtos para a venda (entre 1 e 5 produtos)
            qtd_produtos = random.randint(1, 5)
            produtos_venda = random.sample(produtos_empresa, min(qtd_produtos, len(produtos_empresa)))
            
            valor_total = Decimal('0')
            itens_venda = []
            
            # Calcular valor da venda
            for produto in produtos_venda:
                quantidade = random.randint(1, 10)
                preco_unitario = produto.preco_venda
                valor_item = quantidade * preco_unitario
                valor_total += valor_item
                
                itens_venda.append({
                    "id_produto": produto.id_produto,
                    "descricao": produto.nome,
                    "quantidade": quantidade,
                    "preco_unitario": preco_unitario,
                    "valor": valor_item
                })
            
            # Aplicar desconto aleatório (0-10%)
            desconto_percentual = Decimal(str(random.uniform(0, 0.1))).quantize(Decimal('0.01'))
            valor_desconto = (valor_total * desconto_percentual).quantize(Decimal('0.01'))
            valor_liquido = valor_total - valor_desconto
            
            # Criar a venda
            venda = Venda(
                id_empresa=empresa.id_empresa,
                id_cliente=cliente.id_cliente,
                data_venda=data_venda,
                valor_total=valor_total,
                valor_desconto=valor_desconto,
                valor_liquido=valor_liquido,
                status="CONCLUIDA",
                observacoes=f"Venda de teste {data_venda.strftime('%d/%m/%Y')}",
                itens=itens_venda
            )
            
            session.add(venda)
            session.flush()  # Para obter o ID da venda
            todas_vendas.append(venda)
            
            # Criar parcelas para a venda
            num_parcelas = random.choice([1, 2, 3, 6])
            forma_pagamento = random.choice(formas_empresa)
            
            # Distribuir o valor entre as parcelas
            valor_parcela_base = (valor_liquido / Decimal(num_parcelas)).quantize(Decimal('0.01'))
            valor_restante = valor_liquido
            
            for i in range(num_parcelas):
                # Para a última parcela, ajustar qualquer diferença devido a arredondamentos
                if i == num_parcelas - 1:
                    valor_parcela = valor_restante
                else:
                    valor_parcela = valor_parcela_base
                    valor_restante -= valor_parcela
                
                # Calcular a data de vencimento
                dias_prazo = i * 30  # 30 dias entre parcelas
                data_vencimento = data_venda + timedelta(days=dias_prazo)
                
                # Determinar se a parcela está paga ou em aberto
                # Parcelas vencidas ou futuras podem estar em aberto
                parcela_paga = True  # Por padrão, considerar paga
                
                if data_vencimento > HOJE:
                    # Parcelas futuras têm 70% de chance de estarem em aberto
                    parcela_paga = random.random() > 0.7
                elif (HOJE - data_vencimento).days < 60:
                    # Parcelas vencidas há menos de 60 dias têm 30% de chance de estarem em aberto
                    parcela_paga = random.random() > 0.3
                elif (HOJE - data_vencimento).days >= 60:
                    # Parcelas vencidas há mais de 60 dias têm 10% de chance de estarem em aberto
                    parcela_paga = random.random() > 0.1
                
                data_pagamento = None
                if parcela_paga:
                    # Data de pagamento entre a data da venda e a data de vencimento (ou até 5 dias após)
                    dias_apos_venda = random.randint(0, (data_vencimento - data_venda).days + 5)
                    data_pagamento = data_venda + timedelta(days=dias_apos_venda)
                    # Garantir que não seja uma data futura
                    if data_pagamento > HOJE:
                        data_pagamento = min(data_pagamento, HOJE)
                
                # Criar a parcela
                parcela = ParcelaVenda(
                    id_empresa=empresa.id_empresa,
                    id_venda=venda.id_venda,
                    numero_parcela=i + 1,
                    id_forma_pagamento=forma_pagamento.id_forma_pagamento,
                    data_vencimento=data_vencimento,
                    valor=valor_parcela,
                    data_pagamento=data_pagamento,
                    status="PAGA" if parcela_paga else "ABERTA"
                )
                
                session.add(parcela)
                todas_parcelas.append(parcela)
    
    session.commit()
    print(f"✓ {len(todas_vendas)} vendas criadas com {len(todas_parcelas)} parcelas")
    return todas_vendas, todas_parcelas

def criar_lancamentos(
    session: Session,
    empresas: List[Empresa],
    fornecedores: List[Fornecedor],
    categorias: Dict[int, Dict[str, List[Categoria]]],
    centros_custo: Dict[int, List[CentroCusto]],
    contas_bancarias: Dict[int, List[ContaBancaria]],
    formas_pagamento: Dict[int, List[FormaPagamento]]
) -> List[Lancamento]:
    """Cria lançamentos financeiros para as empresas."""
    todos_lancamentos = []
    
    # Agrupar fornecedores por empresa
    fornecedores_por_empresa = {}
    for fornecedor in fornecedores:
        if fornecedor.id_empresa not in fornecedores_por_empresa:
            fornecedores_por_empresa[fornecedor.id_empresa] = []
        fornecedores_por_empresa[fornecedor.id_empresa].append(fornecedor)
    
    for empresa in empresas:
        fornecedores_empresa = fornecedores_por_empresa.get(empresa.id_empresa, [])
        categorias_receita = categorias.get(empresa.id_empresa, {}).get("receita", [])
        categorias_despesa = categorias.get(empresa.id_empresa, {}).get("despesa", [])
        centros_empresa = centros_custo.get(empresa.id_empresa, [])
        contas_empresa = contas_bancarias.get(empresa.id_empresa, [])
        formas_empresa = formas_pagamento.get(empresa.id_empresa, [])
        
        if not categorias_receita or not categorias_despesa or not centros_empresa or not contas_empresa or not formas_empresa:
            continue
        
        # Criar lançamentos para cada mês entre DATA_INICIO e DATA_FIM
        data_atual = DATA_INICIO
        while data_atual <= DATA_FIM:
            # Número de lançamentos por mês varia entre 5 e 15
            num_lancamentos = random.randint(5, 15)
            
            for _ in range(num_lancamentos):
                # Alternar entre receitas e despesas com probabilidade 30/70
                eh_receita = random.random() < 0.3
                
                # Selecionar categoria apropriada
                if eh_receita:
                    categoria = random.choice(categorias_receita)
                    tipo = "RECEITA"
                    descricao = f"Receita de {categoria.nome.lower()}"
                    # Receitas geralmente são de valores maiores
                    valor = Decimal(str(random.uniform(500, 10000))).quantize(Decimal('0.01'))
                    # Maior probabilidade de estar pago
                    status_pagamento = random.choices(
                        ["PAGO", "ABERTO", "ATRASADO"],
                        weights=[0.85, 0.1, 0.05],
                        k=1
                    )[0]
                    # Normalmente sem fornecedor associado
                    id_fornecedor = None
                else:
                    categoria = random.choice(categorias_despesa)
                    tipo = "DESPESA"
                    # 80% das despesas têm fornecedor se houver fornecedores disponíveis
                    if fornecedores_empresa and random.random() < 0.8:
                        fornecedor = random.choice(fornecedores_empresa)
                        id_fornecedor = fornecedor.id_fornecedor
                        descricao = f"Pagamento para {fornecedor.nome_fantasia} - {categoria.nome}"
                    else:
                        id_fornecedor = None
                        descricao = f"Despesa de {categoria.nome.lower()}"
                    
                    # Despesas geralmente são de valores menores
                    valor = Decimal(str(random.uniform(50, 5000))).quantize(Decimal('0.01'))
                    # Probabilidade balanceada de status
                    status_pagamento = random.choices(
                        ["PAGO", "ABERTO", "ATRASADO"],
                        weights=[0.6, 0.3, 0.1],
                        k=1
                    )[0]
                
                # Selecionar forma de pagamento
                forma_pagamento = random.choice(formas_empresa)
                # Selecionar centro de custo
                centro_custo = random.choice(centros_empresa)
                # Selecionar conta bancária (se pago)
                id_conta_bancaria = forma_pagamento.id_conta_bancaria if forma_pagamento.id_conta_bancaria else (
                    random.choice(contas_empresa).id_conta_bancaria if status_pagamento == "PAGO" else None
                )
                
                # Gerar datas aleatórias dentro do mês atual
                ultimo_dia_mes = (data_atual.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                data_emissao = data_aleatoria(data_atual, ultimo_dia_mes)
                
                # Vencimento entre 0 e 30 dias após emissão
                dias_ate_vencimento = random.randint(0, 30)
                data_vencimento = data_emissao + timedelta(days=dias_ate_vencimento)
                
                # Data de pagamento
                data_pagamento = None
                if status_pagamento == "PAGO":
                    # Pagamento entre a emissão e 5 dias após o vencimento
                    dias_apos_emissao = random.randint(0, (data_vencimento - data_emissao).days + 5)
                    data_pagamento = data_emissao + timedelta(days=dias_apos_emissao)
                    
                    # Garantir que o pagamento não seja no futuro
                    if data_pagamento > HOJE:
                        if random.random() < 0.7:  # 70% de chance de ter sido pago até hoje
                            data_pagamento = HOJE - timedelta(days=random.randint(0, 7))
                        else:
                            # Muda para não pago
                            data_pagamento = None
                            status_pagamento = "ABERTO" if data_vencimento >= HOJE else "ATRASADO"
                
                # Status atrasado apenas para vencidos e não pagos
                if status_pagamento == "ATRASADO" and data_vencimento > HOJE:
                    data_vencimento = HOJE - timedelta(days=random.randint(1, 30))
                
                # Status aberto mas já vencido
                if status_pagamento == "ABERTO" and data_vencimento < HOJE:
                    status_pagamento = "ATRASADO"
                
                # Criar lançamento
                lancamento = Lancamento(
                    id_empresa=empresa.id_empresa,
                    tipo=tipo,
                    descricao=descricao,
                    valor=valor,
                    data_emissao=data_emissao,
                    data_vencimento=data_vencimento,
                    data_pagamento=data_pagamento,
                    id_categoria=categoria.id_categoria,
                    id_centro_custo=centro_custo.id_centro_custo,
                    id_forma_pagamento=forma_pagamento.id_forma_pagamento,
                    id_conta_bancaria=id_conta_bancaria,
                    id_fornecedor=id_fornecedor,
                    status=status_pagamento,
                    observacoes=f"Lançamento de teste {data_emissao.strftime('%m/%Y')}" if random.random() < 0.3 else None
                )
                
                session.add(lancamento)
                todos_lancamentos.append(lancamento)
            
            # Avançar para o próximo mês
            if data_atual.month == 12:
                data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
            else:
                data_atual = data_atual.replace(month=data_atual.month + 1)
    
    session.commit()
    print(f"✓ {len(todos_lancamentos)} lançamentos criados")
    return todos_lancamentos

def criar_transferencias(session: Session, empresas: List[Empresa], contas_bancarias: Dict[int, List[ContaBancaria]]) -> List[Lancamento]:
    """Cria transferências entre contas bancárias."""
    transferencias = []
    
    for empresa in empresas:
        contas_empresa = contas_bancarias.get(empresa.id_empresa, [])
        
        if len(contas_empresa) < 2:
            continue  # Precisa de pelo menos 2 contas para transferência
        
        # Criar algumas transferências (entre 10 e 20 por empresa)
        num_transferencias = random.randint(10, 20)
        
        for _ in range(num_transferencias):
            # Selecionar duas contas diferentes
            conta_origem, conta_destino = random.sample(contas_empresa, 2)
            
            # Gerar data aleatória
            data_transferencia = data_aleatoria(DATA_INICIO, DATA_FIM)
            
            # Gerar valor aleatório
            valor = Decimal(str(random.uniform(100, 5000))).quantize(Decimal('0.01'))
            
            # Criar lançamento de saída
            saida = Lancamento(
                id_empresa=empresa.id_empresa,
                tipo="TRANSFERENCIA_SAIDA",
                descricao=f"Transferência para {conta_destino.banco} - {conta_destino.tipo}",
                valor=valor,
                data_emissao=data_transferencia,
                data_vencimento=data_transferencia,
                data_pagamento=data_transferencia,
                id_categoria=None,
                id_centro_custo=None,
                id_forma_pagamento=None,
                id_conta_bancaria=conta_origem.id_conta_bancaria,
                id_conta_destino=conta_destino.id_conta_bancaria,
                id_fornecedor=None,
                status="PAGO",
                observacoes=f"Transferência entre contas {data_transferencia.strftime('%d/%m/%Y')}"
            )
            
            # Criar lançamento de entrada
            entrada = Lancamento(
                id_empresa=empresa.id_empresa,
                tipo="TRANSFERENCIA_ENTRADA",
                descricao=f"Transferência de {conta_origem.banco} - {conta_origem.tipo}",
                valor=valor,
                data_emissao=data_transferencia,
                data_vencimento=data_transferencia,
                data_pagamento=data_transferencia,
                id_categoria=None,
                id_centro_custo=None,
                id_forma_pagamento=None,
                id_conta_bancaria=conta_destino.id_conta_bancaria,
                id_conta_origem=conta_origem.id_conta_bancaria,
                id_fornecedor=None,
                status="PAGO",
                observacoes=f"Transferência entre contas {data_transferencia.strftime('%d/%m/%Y')}"
            )
            
            session.add(saida)
            session.add(entrada)
            transferencias.extend([saida, entrada])
    
    session.commit()
    print(f"✓ {len(transferencias)} lançamentos de transferência criados")
    return transferencias

def main():
    """Função principal que executa o seed de dados."""
    try:
        print("Iniciando seed de dados para o CCONTROL-M...")
        
        # Criar todas as tabelas se não existirem
        create_all_tables()
        
        # Criar uma sessão com o banco de dados usando a engine síncrona
        from app.database import engine, SessionLocal
        
        # Criar sessão
        session = SessionLocal()
        
        try:
            # Criar empresas
            empresas = criar_empresas(session)
            
            # Criar usuários
            usuarios = criar_usuarios(session, empresas)
            
            # Criar clientes
            clientes = criar_clientes(session, empresas)
            
            # Criar fornecedores
            fornecedores = criar_fornecedores(session, empresas)
            
            # Criar categorias
            categorias = criar_categorias(session, empresas)
            
            # Criar centros de custo
            centros_custo = criar_centros_custo(session, empresas)
            
            # Criar contas bancárias
            contas_bancarias = criar_contas_bancarias(session, empresas)
            
            # Criar formas de pagamento
            formas_pagamento = criar_formas_pagamento(session, empresas, contas_bancarias)
            
            # Criar produtos
            produtos = criar_produtos(session, empresas)
            
            # Criar vendas com parcelas
            vendas, parcelas_venda = criar_vendas_com_parcelas(
                session, empresas, clientes, produtos, formas_pagamento
            )
            
            # Criar lançamentos
            lancamentos = criar_lancamentos(
                session, empresas, fornecedores, categorias, 
                centros_custo, contas_bancarias, formas_pagamento
            )
            
            # Criar transferências
            transferencias = criar_transferencias(session, empresas, contas_bancarias)
            
            # Commit final para garantir que todas as alterações foram salvas
            session.commit()
            
            print("Processo de seed de dados concluído com sucesso!")
        except Exception as e:
            session.rollback()
            print(f"Erro durante o processo de seed: {str(e)}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        print(f"Erro ao iniciar o processo de seed: {str(e)}")
        raise
    finally:
        print("Processo de seed finalizado.")

if __name__ == "__main__":
    main() 