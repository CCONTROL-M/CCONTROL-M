import redis.asyncio as redis
from typing import AsyncGenerator

from app.config.settings import settings


# Cliente Redis assíncrono
_redis_client = None


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    Retorna uma conexão com o Redis.
    Cria o cliente se ainda não existir.
    """
    global _redis_client
    
    if _redis_client is None:
        # Cria um novo cliente Redis se não existir
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,  # Decodifica respostas para string
            socket_timeout=5.0,     # Timeout para operações
            socket_connect_timeout=5.0,  # Timeout para conexão
            retry_on_timeout=True,  # Tenta novamente em caso de timeout
        )
        
        try:
            # Teste de conexão
            await _redis_client.ping()
        except (redis.ConnectionError, redis.TimeoutError) as e:
            # Se a conexão falhar, desativa o Redis
            _redis_client = None
            # Em produção, poderia logar o erro
            print(f"Erro ao conectar ao Redis: {e}")
    
    # Se o cliente foi inicializado corretamente, retorna
    if _redis_client is not None:
        yield _redis_client
    else:
        # Implementação de fallback (em memória)
        # Isso é usado apenas se o Redis não estiver disponível
        # Não é recomendado para produção, pois não funciona com múltiplas instâncias
        from app.core.memory_store import MemoryStore
        yield MemoryStore() 