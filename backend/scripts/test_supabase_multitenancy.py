#!/usr/bin/env python
"""
Script para testar a integração da multilocação com Supabase.
Este script realiza testes básicos para verificar se as políticas RLS estão funcionando corretamente.
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from pprint import pprint

# Adicionar diretório pai ao path para importar configurações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config.settings import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# URLs e configurações do Supabase
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_ANON_KEY
API_URL = f"{SUPABASE_URL}/rest/v1"

# Empresas para teste
EMPRESA_1 = {"id": 1, "nome": "Empresa 1 (Teste)"}
EMPRESA_2 = {"id": 2, "nome": "Empresa 2 (Teste)"}


def login_supabase(email, password):
    """
    Realiza login no Supabase e retorna token de autenticação
    
    Args:
        email: Email do usuário
        password: Senha do usuário
        
    Returns:
        dict: Tokens de autenticação
    """
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro ao fazer login: {e}")
        logger.error(f"Detalhes: {response.text}")
        return None


def get_headers(auth_token):
    """
    Cria headers para requisições autenticadas
    
    Args:
        auth_token: Token de autenticação
        
    Returns:
        dict: Headers para requisições
    """
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


def test_list_clientes(auth_token, expected_count=None):
    """
    Testa a listagem de clientes
    
    Args:
        auth_token: Token de autenticação
        expected_count: Número esperado de clientes (opcional)
        
    Returns:
        list: Lista de clientes
    """
    headers = get_headers(auth_token)
    url = f"{API_URL}/clientes"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        clientes = response.json()
        
        logger.info(f"Total de clientes: {len(clientes)}")
        if expected_count is not None:
            assert len(clientes) == expected_count, f"Esperado {expected_count} clientes, obtido {len(clientes)}"
            logger.info("✅ Teste de contagem de clientes passou!")
        
        # Exibir dados de exemplo
        if clientes:
            logger.info(f"Exemplo de cliente: {json.dumps(clientes[0], indent=2, ensure_ascii=False)}")
        
        return clientes
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro ao listar clientes: {e}")
        logger.error(f"Detalhes: {response.text}")
        return None
    except AssertionError as e:
        logger.error(f"❌ Teste falhou: {e}")
        return None


def test_create_cliente(auth_token, nome, empresa_id=None):
    """
    Testa a criação de um cliente
    
    Args:
        auth_token: Token de autenticação
        nome: Nome do cliente
        empresa_id: ID da empresa (opcional, pois deve ser inferido do token)
        
    Returns:
        dict: Cliente criado
    """
    headers = get_headers(auth_token)
    url = f"{API_URL}/clientes"
    
    # Dados do cliente com data atual para facilitar identificação
    payload = {
        "nome": f"{nome} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "email": f"teste_{datetime.now().strftime('%Y%m%d%H%M%S')}@teste.com",
        "telefone": "(99) 99999-9999",
        "endereco": "Endereço de teste",
    }
    
    # Adicionar empresa_id apenas se fornecido (para testar se o middleware está funcionando)
    if empresa_id:
        payload["id_empresa"] = empresa_id
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        cliente = response.json()[0]  # Supabase retorna array com um objeto
        
        logger.info(f"Cliente criado: {json.dumps(cliente, indent=2, ensure_ascii=False)}")
        
        # Verificar se id_empresa foi inserido corretamente
        if empresa_id:
            assert cliente["id_empresa"] == empresa_id, "ID da empresa não corresponde"
            logger.info("✅ Teste de criação de cliente com ID de empresa específico passou!")
        else:
            logger.info(f"ID da empresa associada: {cliente.get('id_empresa')}")
            logger.info("✅ Teste de criação de cliente através do middleware passou!")
        
        return cliente
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro ao criar cliente: {e}")
        logger.error(f"Detalhes: {response.text}")
        return None
    except AssertionError as e:
        logger.error(f"❌ Teste falhou: {e}")
        return None


def test_cross_tenant_access(auth_token, client_id, expect_success=False):
    """
    Testa acesso a dados de outro tenant
    
    Args:
        auth_token: Token de autenticação
        client_id: ID do cliente a ser acessado
        expect_success: Se o teste deve passar (padrão: deve falhar)
        
    Returns:
        bool: Resultado do teste
    """
    headers = get_headers(auth_token)
    url = f"{API_URL}/clientes?id=eq.{client_id}"
    
    try:
        response = requests.get(url, headers=headers)
        
        if expect_success:
            response.raise_for_status()
            cliente = response.json()
            logger.info(f"Acesso permitido ao cliente: {json.dumps(cliente, indent=2, ensure_ascii=False)}")
            logger.info("✅ Teste de acesso cross-tenant permitido passou!")
            return True
        else:
            # Deveria falhar com 403 ou 404
            if response.status_code in [403, 404]:
                logger.info(f"✅ Acesso negado como esperado (status code: {response.status_code})")
                return True
            else:
                logger.error(f"❌ Teste falhou: Esperava restrição de acesso, mas obteve status {response.status_code}")
                logger.error(f"Resposta: {response.text}")
                return False
    except requests.exceptions.HTTPError as e:
        if not expect_success:
            logger.info(f"✅ Acesso negado como esperado: {e}")
            return True
        else:
            logger.error(f"❌ Teste falhou: {e}")
            logger.error(f"Detalhes: {response.text}")
            return False


def run_tests():
    """
    Executa todos os testes de multilocação com Supabase
    """
    logger.info("=== INICIANDO TESTES DE MULTILOCAÇÃO COM SUPABASE ===")
    
    # Usuários para teste (substitua pelos usuários reais)
    user1 = {"email": "user1@example.com", "password": "senha_segura_1"}
    user2 = {"email": "user2@example.com", "password": "senha_segura_2"}
    
    # Login com usuário 1 (empresa 1)
    logger.info(f"Logando como usuário da empresa 1: {user1['email']}")
    auth1 = login_supabase(user1["email"], user1["password"])
    if not auth1:
        logger.error("❌ Falha ao autenticar usuário 1. Encerrando testes.")
        return
    
    # Login com usuário 2 (empresa 2)
    logger.info(f"Logando como usuário da empresa 2: {user2['email']}")
    auth2 = login_supabase(user2["email"], user2["password"])
    if not auth2:
        logger.error("❌ Falha ao autenticar usuário 2. Continuando apenas com usuário 1.")
    
    # Token de acesso
    token1 = auth1["access_token"]
    token2 = auth2["access_token"] if auth2 else None
    
    # === Teste 1: Listar clientes (Empresa 1) ===
    logger.info("\n=== Teste 1: Listar clientes (Empresa 1) ===")
    clientes_empresa1 = test_list_clientes(token1)
    
    # === Teste 2: Criar cliente (Empresa 1) ===
    logger.info("\n=== Teste 2: Criar cliente (Empresa 1) ===")
    novo_cliente1 = test_create_cliente(token1, "Cliente Teste Empresa 1")
    
    # Se temos o segundo usuário, executar testes para a empresa 2
    if token2:
        # === Teste 3: Listar clientes (Empresa 2) ===
        logger.info("\n=== Teste 3: Listar clientes (Empresa 2) ===")
        clientes_empresa2 = test_list_clientes(token2)
        
        # === Teste 4: Criar cliente (Empresa 2) ===
        logger.info("\n=== Teste 4: Criar cliente (Empresa 2) ===")
        novo_cliente2 = test_create_cliente(token2, "Cliente Teste Empresa 2")
        
        # === Teste 5: Tentar acessar cliente da Empresa 1 com usuário da Empresa 2 ===
        if novo_cliente1:
            logger.info("\n=== Teste 5: Tentar acessar cliente da Empresa 1 com usuário da Empresa 2 ===")
            test_cross_tenant_access(token2, novo_cliente1["id"], expect_success=False)
        
        # === Teste 6: Tentar acessar cliente da Empresa 2 com usuário da Empresa 1 ===
        if novo_cliente2:
            logger.info("\n=== Teste 6: Tentar acessar cliente da Empresa 2 com usuário da Empresa 1 ===")
            test_cross_tenant_access(token1, novo_cliente2["id"], expect_success=False)
    
    logger.info("\n=== TESTES DE MULTILOCAÇÃO COM SUPABASE CONCLUÍDOS ===")


if __name__ == "__main__":
    run_tests() 