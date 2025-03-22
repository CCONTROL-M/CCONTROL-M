import time
from collections import defaultdict
from typing import Optional, Dict, Any, Union, List
import asyncio


class MemoryStore:
    """
    Implementação simples de armazenamento em memória para ser usado
    como fallback quando o Redis não está disponível.
    
    Implementa apenas os métodos Redis que são usados pelo sistema.
    
    AVISO: Isso NÃO é recomendado para produção com múltiplas instâncias,
    pois os dados são armazenados apenas na memória da instância atual.
    """
    
    def __init__(self):
        # Armazena os valores e seus timestamps de expiração
        self._data: Dict[str, Any] = {}
        self._expires: Dict[str, int] = {}
        
        # Para simular listas
        self._lists: Dict[str, List[str]] = defaultdict(list)
        
        # Para simular hashes
        self._hashes: Dict[str, Dict[str, str]] = defaultdict(dict)
        
        # Iniciar tarefa de limpeza periódica
        asyncio.create_task(self._cleanup_expired_keys())
    
    async def _cleanup_expired_keys(self):
        """
        Limpa periodicamente as chaves expiradas para evitar vazamento de memória.
        """
        while True:
            current_time = int(time.time())
            
            # Encontrar chaves expiradas
            expired_keys = [
                key for key, expire_time in self._expires.items()
                if expire_time <= current_time
            ]
            
            # Remover chaves expiradas
            for key in expired_keys:
                self._data.pop(key, None)
                self._expires.pop(key, None)
                self._lists.pop(key, None)
                self._hashes.pop(key, None)
            
            # Verificar a cada 60 segundos
            await asyncio.sleep(60)
    
    def _check_expiry(self, key: str) -> bool:
        """Verifica se uma chave expirou e a remove se necessário."""
        if key in self._expires:
            if int(time.time()) > self._expires[key]:
                # Se expirou, remove todas as referências
                self._data.pop(key, None)
                self._expires.pop(key, None)
                self._lists.pop(key, None)
                self._hashes.pop(key, None)
                return False
        return True
    
    ### Métodos básicos ###
    
    async def get(self, key: str) -> Optional[str]:
        """Obtém o valor de uma chave."""
        if key in self._data and self._check_expiry(key):
            return self._data[key]
        return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Define o valor de uma chave com tempo de expiração opcional."""
        self._data[key] = value
        
        if ex is not None:
            self._expires[key] = int(time.time()) + ex
        elif key in self._expires:
            # Remover a expiração se não especificada
            del self._expires[key]
            
        return True
    
    async def delete(self, key: str) -> int:
        """Remove uma chave e retorna o número de chaves removidas."""
        if key in self._data:
            del self._data[key]
            self._expires.pop(key, None)
            self._lists.pop(key, None)
            self._hashes.pop(key, None)
            return 1
        return 0
    
    ### Métodos para contadores e expiração ###
    
    async def incr(self, key: str) -> int:
        """Incrementa o valor de uma chave e retorna o novo valor."""
        if key in self._data and self._check_expiry(key):
            try:
                value = int(self._data[key]) + 1
                self._data[key] = str(value)
                return value
            except (ValueError, TypeError):
                # Se não for um número, substitui por 1
                self._data[key] = "1"
                return 1
        else:
            # Se a chave não existir, cria com valor 1
            self._data[key] = "1"
            return 1
    
    async def expire(self, key: str, seconds: int) -> int:
        """Define a expiração de uma chave."""
        if key in self._data:
            self._expires[key] = int(time.time()) + seconds
            return 1
        return 0
    
    async def ttl(self, key: str) -> int:
        """Retorna o tempo de vida restante de uma chave em segundos."""
        if key in self._expires and self._check_expiry(key):
            return max(0, self._expires[key] - int(time.time()))
        elif key in self._data:
            return -1  # A chave existe mas não expira
        return -2  # A chave não existe
    
    ### Métodos para listas ###
    
    async def lpush(self, key: str, *values) -> int:
        """Adiciona valores ao início de uma lista."""
        if not self._check_expiry(key):
            self._lists[key] = []
            
        for value in values:
            self._lists[key].insert(0, str(value))
        
        return len(self._lists[key])
    
    async def rpush(self, key: str, *values) -> int:
        """Adiciona valores ao final de uma lista."""
        if not self._check_expiry(key):
            self._lists[key] = []
            
        for value in values:
            self._lists[key].append(str(value))
        
        return len(self._lists[key])
    
    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Obtém um intervalo de elementos de uma lista."""
        if key in self._lists and self._check_expiry(key):
            # Ajustar índice negativo como o Redis
            if end < 0 and abs(end) <= len(self._lists[key]):
                end = len(self._lists[key]) + end
            elif end < 0:
                end = -1
                
            if end == -1:
                end = len(self._lists[key]) - 1
                
            return self._lists[key][start:end+1]
        return []
    
    ### Métodos para hash ###
    
    async def hset(self, key: str, field: str, value: str) -> int:
        """Define o valor de um campo em um hash."""
        if not self._check_expiry(key):
            self._hashes[key] = {}
            
        is_new = field not in self._hashes[key]
        self._hashes[key][field] = str(value)
        
        return 1 if is_new else 0
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Obtém o valor de um campo em um hash."""
        if key in self._hashes and field in self._hashes[key] and self._check_expiry(key):
            return self._hashes[key][field]
        return None
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        """Obtém todos os campos e valores de um hash."""
        if key in self._hashes and self._check_expiry(key):
            return dict(self._hashes[key])
        return {}
    
    ### Métodos para a manipulação de chaves ###
    
    async def keys(self, pattern: str) -> List[str]:
        """
        Retorna todas as chaves que correspondem ao padrão.
        Implementação simplificada que suporta apenas * no final.
        """
        if pattern == "*":
            # Retorna todas as chaves não expiradas
            all_keys = set(self._data.keys()) | set(self._lists.keys()) | set(self._hashes.keys())
            return [key for key in all_keys if self._check_expiry(key)]
        
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            all_keys = set(self._data.keys()) | set(self._lists.keys()) | set(self._hashes.keys())
            return [key for key in all_keys if key.startswith(prefix) and self._check_expiry(key)]
        
        # Verificação exata
        if pattern in self._data and self._check_expiry(pattern):
            return [pattern]
        
        return []
    
    async def ping(self) -> bool:
        """Verifica se o serviço está disponível."""
        return True 