import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Union, List, Set
import os
import sys
from enum import Enum

from fastapi import Request
from pydantic import BaseModel, Field

from app.config.settings import settings

# Criar diretório de logs se não existir
LOG_DIR = settings.LOG_DIR if hasattr(settings, "LOG_DIR") else "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configuração do logger de auditoria
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Configurar handlers de arquivo e console se não existirem
if not audit_logger.handlers:
    # Handler para arquivo de auditoria geral
    file_handler = logging.FileHandler(f"{LOG_DIR}/audit.log")
    file_handler.setLevel(logging.INFO)
    
    # Handler específico para ações sensíveis
    sensitive_handler = logging.FileHandler(f"{LOG_DIR}/sensitive_actions.log")
    sensitive_handler.setLevel(logging.INFO)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Definir formatação para os logs - removendo o campo request_id que está causando o erro
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )
    
    file_handler.setFormatter(formatter)
    sensitive_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers ao logger
    audit_logger.addHandler(file_handler)
    audit_logger.addHandler(sensitive_handler)
    audit_logger.addHandler(console_handler)


class AuditActionType(str, Enum):
    """Tipos de ações para auditoria"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    AUTH = "auth"
    ADMIN = "admin"
    EXPORT = "export"
    IMPORT = "import"
    PAYMENT = "payment"
    FINANCIAL = "financial"
    CONFIG = "config"


class AuditSeverity(str, Enum):
    """Níveis de severidade para eventos de auditoria"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLog(BaseModel):
    """Modelo para logs de auditoria"""
    request_id: str = Field(..., description="ID único para a requisição")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da requisição")
    user_id: Optional[str] = Field(None, description="ID do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")
    empresa_id: Optional[str] = Field(None, description="ID da empresa")
    method: str = Field(..., description="Método HTTP")
    url: str = Field(..., description="URL da requisição")
    path: str = Field(..., description="Caminho da requisição")
    status_code: int = Field(..., description="Código de status HTTP")
    response_time_ms: float = Field(..., description="Tempo de resposta em milissegundos")
    ip_address: str = Field(..., description="Endereço IP do cliente")
    user_agent: Optional[str] = Field(None, description="User-Agent do cliente")
    request_body: Optional[Dict[str, Any]] = Field(None, description="Corpo da requisição")
    query_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros de consulta")
    path_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros de caminho")
    headers: Optional[Dict[str, str]] = Field(None, description="Cabeçalhos da requisição")
    error: Optional[str] = Field(None, description="Erro ocorrido, se houver")
    action_type: Optional[AuditActionType] = Field(None, description="Tipo de ação realizada")
    severity: AuditSeverity = Field(default=AuditSeverity.LOW, description="Severidade do evento")
    resource_type: Optional[str] = Field(None, description="Tipo de recurso afetado (tabela/entidade)")
    resource_id: Optional[str] = Field(None, description="ID do recurso afetado")
    changes: Optional[Dict[str, Any]] = Field(None, description="Mudanças realizadas (antes/depois)")
    is_sensitive: bool = Field(default=False, description="Se é uma ação sensível")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SensitiveOperationAudit(BaseModel):
    """Modelo para auditoria detalhada de operações sensíveis"""
    audit_id: str = Field(..., description="ID único do registro de auditoria")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da operação")
    user_id: str = Field(..., description="ID do usuário que realizou a operação")
    user_email: str = Field(..., description="Email do usuário")
    empresa_id: Optional[str] = Field(None, description="ID da empresa")
    operation: str = Field(..., description="Operação realizada")
    resource_type: str = Field(..., description="Tipo de recurso (tabela/entidade)")
    resource_id: str = Field(..., description="ID do recurso afetado")
    previous_state: Optional[Dict[str, Any]] = Field(None, description="Estado anterior")
    new_state: Optional[Dict[str, Any]] = Field(None, description="Novo estado")
    ip_address: str = Field(..., description="Endereço IP do cliente")
    justification: Optional[str] = Field(None, description="Justificativa para a operação")
    severity: AuditSeverity = Field(default=AuditSeverity.HIGH, description="Severidade da operação")
    additional_info: Optional[Dict[str, Any]] = Field(None, description="Informações adicionais")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AuditLogger:
    """Classe avançada para gerenciar logs de auditoria"""
    
    def __init__(self):
        self.logger = audit_logger
        
        # Lista de campos sensíveis por categoria
        self.sensitive_fields = {
            "auth": set(["password", "senha", "token", "secret", "api_key", "apikey", "refresh_token", "access_token"]),
            "personal": set(["cpf", "cnpj", "rg", "data_nascimento", "endereco", "telefone", "celular"]),
            "financial": set(["credit_card", "cartao_credito", "cartao", "cvv", "expiry", "validade", "conta", "agencia", "saldo"]),
            "all": set(settings.SENSITIVE_FIELDS)
        }
        
        # Define ações sensíveis por rota/método
        self.sensitive_routes = [
            # Usuários e permissões
            {"path": r"/api/v1/usuarios", "methods": ["POST", "PUT", "DELETE"]},
            {"path": r"/api/v1/permissoes", "methods": ["POST", "PUT", "DELETE"]},
            
            # Autenticação
            {"path": r"/api/v1/auth/token", "methods": ["POST"]},
            {"path": r"/api/v1/auth/reset-password", "methods": ["POST"]},
            
            # Configurações da empresa
            {"path": r"/api/v1/empresas", "methods": ["POST", "PUT", "DELETE"]},
            
            # Operações financeiras
            {"path": r"/api/v1/lancamentos", "methods": ["POST", "PUT", "DELETE"]},
            {"path": r"/api/v1/contas_bancarias", "methods": ["POST", "PUT", "DELETE"]},
            
            # Exportação/Importação
            {"path": r"/api/v1/.*/exportar", "methods": ["GET", "POST"]},
            {"path": r"/api/v1/.*/importar", "methods": ["POST"]},
        ]
    
    def sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove informações sensíveis dos cabeçalhos"""
        sensitive_headers = ["authorization", "cookie", "x-api-key", "x-token", "refresh-token"]
        return {
            k: "**REDACTED**" if k.lower() in sensitive_headers else v
            for k, v in headers.items()
        }
    
    def sanitize_body(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Remove informações sensíveis do corpo da requisição"""
        if not body:
            return body
            
        # Combinar todos os campos sensíveis
        all_sensitive_fields = set()
        for field_set in self.sensitive_fields.values():
            all_sensitive_fields.update(field_set)
            
        sanitized = {}
        self._sanitize_dict(body, sanitized, all_sensitive_fields)
        return sanitized
    
    def _sanitize_dict(self, data: Dict[str, Any], result: Dict[str, Any], sensitive_fields: Set[str]) -> None:
        """Sanitiza recursivamente um dicionário, removendo campos sensíveis"""
        for k, v in data.items():
            if any(sensitive in k.lower() for sensitive in sensitive_fields):
                result[k] = "**REDACTED**"
            elif isinstance(v, dict):
                result[k] = {}
                self._sanitize_dict(v, result[k], sensitive_fields)
            elif isinstance(v, list):
                result[k] = []
                for item in v:
                    if isinstance(item, dict):
                        item_result = {}
                        self._sanitize_dict(item, item_result, sensitive_fields)
                        result[k].append(item_result)
                    else:
                        result[k].append(item)
            else:
                result[k] = v
    
    def get_client_ip(self, request: Request) -> str:
        """Obtém o IP real do cliente, considerando proxies"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get first IP from X-Forwarded-For as it should be the client IP
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_sensitive_operation(self, method: str, path: str) -> bool:
        """Verifica se uma operação é considerada sensível com base na rota e método"""
        import re
        
        for route in self.sensitive_routes:
            if re.match(route["path"], path) and method in route["methods"]:
                return True
                
        return False
    
    def _get_action_type(self, method: str, path: str) -> AuditActionType:
        """Determina o tipo de ação com base no método HTTP e caminho"""
        if method == "GET":
            return AuditActionType.READ
        elif method == "POST":
            if "auth" in path:
                return AuditActionType.AUTH
            elif "exportar" in path:
                return AuditActionType.EXPORT
            elif "importar" in path:
                return AuditActionType.IMPORT
            else:
                return AuditActionType.CREATE
        elif method == "PUT" or method == "PATCH":
            return AuditActionType.UPDATE
        elif method == "DELETE":
            return AuditActionType.DELETE
        else:
            return None
            
    def _get_severity(self, method: str, path: str, status_code: int) -> AuditSeverity:
        """Determina a severidade com base no método, caminho e código de status"""
        # Erros sempre têm severidade pelo menos média
        if status_code >= 400:
            return AuditSeverity.MEDIUM
            
        # Erros de servidor têm severidade alta
        if status_code >= 500:
            return AuditSeverity.HIGH
            
        # Operações sensíveis têm severidade alta
        if self._is_sensitive_operation(method, path):
            return AuditSeverity.HIGH
            
        # Operações de deleção têm severidade média
        if method == "DELETE":
            return AuditSeverity.MEDIUM
            
        # Operações financeiras têm severidade média
        if any(term in path for term in ["lancamentos", "contas", "pagamentos", "financeiro"]):
            return AuditSeverity.MEDIUM
            
        # Outras operações têm severidade baixa
        return AuditSeverity.LOW
    
    def _extract_resource_info(self, path: str, method: str) -> tuple:
        """Extrai informações sobre o recurso afetado"""
        import re
        
        # Padrão para extrair o tipo de recurso e ID do caminho
        pattern = r"/api/v\d+/([^/]+)(?:/([^/]+))?.*"
        match = re.match(pattern, path)
        
        if match:
            resource_type = match.group(1)
            resource_id = match.group(2) if match.group(2) and not match.group(2).startswith("?") else None
            
            return resource_type, resource_id
            
        return None, None
    
    async def log_request(
        self,
        request: Request,
        status_code: int,
        response_time: float,
        error: Optional[str] = None,
        user_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Registra informações sobre uma requisição HTTP."""
        # Extrair informações da requisição
        method = request.method
        url = str(request.url)
        path = request.url.path
        
        # Parâmetros de consulta
        query_params = dict(request.query_params)
        
        # Parâmetros de caminho
        path_params = dict(request.path_params)
        
        # Cabeçalhos
        headers = self.sanitize_headers(dict(request.headers))
        
        # User Agent
        user_agent = request.headers.get("User-Agent")
        
        # Corpo da requisição (se aplicável)
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                if request.headers.get("Content-Type", "").startswith("application/json"):
                    # Evitar o uso direto de await em request.body()
                    # Em vez disso, assumir que o corpo já foi consumido ou não é necessário
                    request_body = {"info": "Body not captured to avoid async_generator issue"}
            except Exception as e:
                request_body = {"error": f"Failed to parse request body: {str(e)}"}
        
        # IP do cliente
        ip_address = self.get_client_ip(request)
        
        # Determinar o tipo de ação, severidade e informações de recurso
        action_type = self._get_action_type(method, path)
        severity = self._get_severity(method, path, status_code)
        resource_type, resource_id = self._extract_resource_info(path, method)
        is_sensitive = self._is_sensitive_operation(method, path)
        
        # Criar ID de auditoria
        audit_id = str(uuid.uuid4())
        
        # Criar log de auditoria
        audit_data = AuditLog(
            request_id=audit_id,
            method=method,
            url=url,
            path=path,
            status_code=status_code,
            response_time_ms=response_time,
            ip_address=ip_address,
            user_agent=user_agent,
            request_body=request_body,
            query_params=query_params,
            path_params=path_params,
            headers=headers,
            error=error,
            action_type=action_type,
            severity=severity,
            resource_type=resource_type,
            resource_id=resource_id,
            is_sensitive=is_sensitive
        )
        
        # Adicionar informações do usuário, se disponíveis
        if user_data:
            audit_data.user_id = user_data.get("id")
            audit_data.user_email = user_data.get("email")
            audit_data.empresa_id = user_data.get("empresa_id")
        
        # Registrar o log
        self.logger.info(json.dumps(audit_data.dict(), default=str))
        
        # Para operações sensíveis, criar um log adicional mais detalhado
        if is_sensitive and user_data:
            # Obter as mudanças (se disponíveis no state da requisição)
            changes = {}
            if hasattr(request.state, "changes"):
                changes = request.state.changes
                
            sensitive_audit = SensitiveOperationAudit(
                audit_id=audit_id,
                user_id=user_data.get("id", "unknown"),
                user_email=user_data.get("email", "unknown"),
                empresa_id=user_data.get("empresa_id"),
                operation=f"{method} {path}",
                resource_type=resource_type or "unknown",
                resource_id=resource_id or "unknown",
                previous_state=changes.get("previous", {}),
                new_state=changes.get("new", {}),
                ip_address=ip_address,
                justification=request.headers.get("X-Justification"),
                severity=severity,
                additional_info={
                    "status_code": status_code,
                    "error": error
                }
            )
            
            # Registrar o log de operação sensível separadamente
            with open(f"{LOG_DIR}/sensitive_actions.log", "a") as sensitive_log:
                sensitive_log.write(json.dumps(sensitive_audit.dict(), default=str) + "\n")
            
        # Se estiver em modo de depuração, registrar logs adicionais
        if settings.DEBUG and error:
            self.logger.error(f"Error during request processing: {error}")

    async def log_sensitive_action(
        self,
        user_data: Dict[str, Any],
        operation: str,
        resource_type: str,
        resource_id: str,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        justification: Optional[str] = None,
        ip_address: str = "unknown",
        additional_info: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.HIGH
    ) -> None:
        """Registra uma ação sensível explicitamente."""
        audit_id = str(uuid.uuid4())
        
        # Sanitizar estados para remover informações sensíveis
        sanitized_previous = None
        sanitized_new = None
        
        if previous_state:
            sanitized_previous = {}
            self._sanitize_dict(previous_state, sanitized_previous, self.sensitive_fields["all"])
            
        if new_state:
            sanitized_new = {}
            self._sanitize_dict(new_state, sanitized_new, self.sensitive_fields["all"])
        
        # Criar registro de auditoria sensível
        sensitive_audit = SensitiveOperationAudit(
            audit_id=audit_id,
            user_id=user_data.get("id", "unknown"),
            user_email=user_data.get("email", "unknown"),
            empresa_id=user_data.get("empresa_id"),
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            previous_state=sanitized_previous,
            new_state=sanitized_new,
            ip_address=ip_address,
            justification=justification,
            severity=severity,
            additional_info=additional_info
        )
        
        # Registrar o log de operação sensível
        with open(f"{LOG_DIR}/sensitive_actions.log", "a") as sensitive_log:
            sensitive_log.write(json.dumps(sensitive_audit.dict(), default=str) + "\n")
            
        # Também registrar no log principal de auditoria
        self.logger.info(json.dumps({
            "type": "sensitive_action",
            "audit_id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_data.get("id", "unknown"),
            "operation": operation,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "severity": severity
        }, default=str))


# Instância do logger de auditoria para uso em middleware
audit_logger_instance = AuditLogger() 