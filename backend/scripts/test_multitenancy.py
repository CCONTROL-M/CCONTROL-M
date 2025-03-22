"""Script para testar o isolamento multi-tenancy entre empresas."""
import os
import sys
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from uuid import UUID

# Adicionar diretório pai ao path para importar configurações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config.settings import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# URL base da API (ajuste conforme necessário)
API_BASE_URL = "http://localhost:8000/api"


def login(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Realiza login na API e retorna o token e informações do usuário.
    
    Args:
        email: Email do usuário
        password: Senha do usuário
        
    Returns:
        Dict com token e informações ou None se falhar
    """
    try:
        url = f"{API_BASE_URL}/auth/login-json"
        payload = {
            "email": email,
            "senha": password
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Erro ao fazer login: {str(e)}")
        return None


def get_resource(resource_path: str, token: str) -> Optional[Dict[str, Any]]:
    """
    Obtém um recurso da API usando o token fornecido.
    
    Args:
        resource_path: Caminho do recurso (ex: '/clientes')
        token: Token JWT de autenticação
        
    Returns:
        Dados do recurso ou None se falhar
    """
    try:
        url = f"{API_BASE_URL}{resource_path}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Erro ao obter recurso {resource_path}: {str(e)}")
        return None


def create_resource(resource_path: str, token: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Cria um recurso na API usando o token fornecido.
    
    Args:
        resource_path: Caminho do recurso (ex: '/clientes')
        token: Token JWT de autenticação
        data: Dados para criar o recurso
        
    Returns:
        Dados do recurso criado ou None se falhar
    """
    try:
        url = f"{API_BASE_URL}{resource_path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Erro ao criar recurso {resource_path}: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Resposta: {e.response.text}")
        return None


def test_cross_tenant_access(token_a: str, token_b: str, resource_id: str, resource_path: str) -> bool:
    """
    Testa acesso entre tenants tentando acessar um recurso de outra empresa.
    
    Args:
        token_a: Token da empresa A
        token_b: Token da empresa B
        resource_id: ID do recurso da empresa A
        resource_path: Caminho base do recurso (ex: '/clientes')
        
    Returns:
        True se o teste passar (acesso negado), False caso contrário
    """
    try:
        # Tentar acessar recurso da empresa A com token da empresa B
        url = f"{API_BASE_URL}{resource_path}/{resource_id}"
        headers = {
            "Authorization": f"Bearer {token_b}"
        }
        
        response = requests.get(url, headers=headers)
        
        # Esperamos um erro 403 (Forbidden) ou 404 (Not Found)
        if response.status_code in [403, 404]:
            logger.info(f"Teste de acesso entre tenants passou! Status: {response.status_code}")
            return True
        else:
            logger.error(f"Teste de acesso entre tenants falhou! Status: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erro ao testar acesso entre tenants: {str(e)}")
        return False


def run_tests():
    """
    Executa os testes de multi-tenancy.
    """
    logger.info("Iniciando testes de multi-tenancy...")
    
    # Credenciais para duas empresas diferentes (ajuste conforme necessário)
    empresa_a = {
        "email": "usuario_empresa_a@exemplo.com",
        "senha": "senha123"
    }
    
    empresa_b = {
        "email": "usuario_empresa_b@exemplo.com",
        "senha": "senha123"
    }
    
    # Login nas duas empresas
    logger.info(f"Fazendo login como usuário da empresa A: {empresa_a['email']}")
    login_a = login(empresa_a["email"], empresa_a["senha"])
    if not login_a:
        logger.error("Falha ao fazer login na empresa A. Verifique as credenciais.")
        return
    
    logger.info(f"Fazendo login como usuário da empresa B: {empresa_b['email']}")
    login_b = login(empresa_b["email"], empresa_b["senha"])
    if not login_b:
        logger.error("Falha ao fazer login na empresa B. Verifique as credenciais.")
        return
    
    token_a = login_a["access_token"]
    token_b = login_b["access_token"]
    
    # Teste 1: Verificar se ambas as empresas podem acessar seus próprios dados
    logger.info("Teste 1: Verificando acesso aos próprios dados...")
    
    clientes_a = get_resource("/clientes/", token_a)
    clientes_b = get_resource("/clientes/", token_b)
    
    if clientes_a and clientes_b:
        logger.info("✅ Teste 1 passou: Ambas as empresas podem acessar seus próprios dados")
    else:
        logger.error("❌ Teste 1 falhou: Problema ao acessar dados")
        return
    
    # Teste 2: Criar cliente em cada empresa
    logger.info("Teste 2: Criando cliente em cada empresa...")
    
    cliente_data_a = {
        "nome": "Cliente Teste Empresa A",
        "cpf_cnpj": "11122233344",
        "contato": "cliente_a@exemplo.com"
    }
    
    cliente_data_b = {
        "nome": "Cliente Teste Empresa B",
        "cpf_cnpj": "55566677788",
        "contato": "cliente_b@exemplo.com"
    }
    
    cliente_a = create_resource("/clientes/", token_a, cliente_data_a)
    cliente_b = create_resource("/clientes/", token_b, cliente_data_b)
    
    if cliente_a and cliente_b:
        logger.info("✅ Teste 2 passou: Clientes criados em ambas as empresas")
    else:
        logger.error("❌ Teste 2 falhou: Problema ao criar clientes")
        return
    
    # Verificar se cada empresa tem o id_empresa correto
    empresa_id_a = login_a["empresa_id"]
    empresa_id_b = login_b["empresa_id"]
    
    if cliente_a.get("id_empresa") == empresa_id_a and cliente_b.get("id_empresa") == empresa_id_b:
        logger.info("✅ Verificação de id_empresa correta: Cada cliente tem o id_empresa correto")
    else:
        logger.error("❌ Verificação de id_empresa falhou: id_empresa incorreto")
        if cliente_a:
            logger.error(f"Cliente A - id_empresa: {cliente_a.get('id_empresa')} | esperado: {empresa_id_a}")
        if cliente_b:
            logger.error(f"Cliente B - id_empresa: {cliente_b.get('id_empresa')} | esperado: {empresa_id_b}")
    
    # Teste 3: Tentar acessar dados entre tenants
    logger.info("Teste 3: Testando acesso entre tenants...")
    
    if cliente_a and cliente_b:
        # Tentar acessar cliente da empresa A com token da empresa B
        cross_access_test = test_cross_tenant_access(
            token_a, token_b, cliente_a["id_cliente"], "/clientes"
        )
        
        if cross_access_test:
            logger.info("✅ Teste 3 passou: Acesso entre tenants bloqueado corretamente")
        else:
            logger.error("❌ Teste 3 falhou: Foi possível acessar dados de outra empresa")
    
    # Teste 4: Verificar se as listagens estão filtradas corretamente
    logger.info("Teste 4: Verificando se listagens estão filtradas por empresa...")
    
    # Buscar todos os clientes novamente para cada empresa
    clientes_a_updated = get_resource("/clientes/", token_a)
    clientes_b_updated = get_resource("/clientes/", token_b)
    
    if clientes_a_updated and clientes_b_updated:
        # Verificar se o cliente A aparece apenas na listagem da empresa A
        cliente_a_in_list_a = any(c["id_cliente"] == cliente_a["id_cliente"] for c in clientes_a_updated["items"])
        cliente_a_in_list_b = any(c["id_cliente"] == cliente_a["id_cliente"] for c in clientes_b_updated["items"])
        
        # Verificar se o cliente B aparece apenas na listagem da empresa B
        cliente_b_in_list_a = any(c["id_cliente"] == cliente_b["id_cliente"] for c in clientes_a_updated["items"])
        cliente_b_in_list_b = any(c["id_cliente"] == cliente_b["id_cliente"] for c in clientes_b_updated["items"])
        
        if cliente_a_in_list_a and not cliente_a_in_list_b and not cliente_b_in_list_a and cliente_b_in_list_b:
            logger.info("✅ Teste 4 passou: Listagens filtradas corretamente por empresa")
        else:
            logger.error("❌ Teste 4 falhou: Problemas com filtro por empresa nas listagens")
            logger.error(f"Cliente A na lista A: {cliente_a_in_list_a} (deve ser True)")
            logger.error(f"Cliente A na lista B: {cliente_a_in_list_b} (deve ser False)")
            logger.error(f"Cliente B na lista A: {cliente_b_in_list_a} (deve ser False)")
            logger.error(f"Cliente B na lista B: {cliente_b_in_list_b} (deve ser True)")
    
    logger.info("Testes de multi-tenancy concluídos!")


if __name__ == "__main__":
    run_tests() 