"""
Configuração e gestão de métricas para o sistema CCONTROL-M.

Implementa estruturas para coleta e exposição de métricas
de observabilidade compatíveis com Prometheus.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import threading
import os
from collections import defaultdict
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST

# Constantes e configurações
METRICS_RETENTION_DAYS = int(os.getenv("METRICS_RETENTION_DAYS", "7"))
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "True").lower() == "true"


class PerfMetrics:
    """
    Armazena métricas de desempenho do sistema.
    
    Fornece estruturas de dados para rastrear métricas
    de performance e disponibilizá-las para sistemas
    de monitoramento externos.
    """
    
    def __init__(self):
        """Inicializa contadores e métricas de performance."""
        # Contadores para requisições
        self.request_count = defaultdict(int)  # Total por rota
        self.request_count_by_method = defaultdict(lambda: defaultdict(int))  # Total por rota+método
        self.request_count_by_status = defaultdict(lambda: defaultdict(int))  # Total por rota+status
        
        # Métricas de latência
        self.request_latency_sum = defaultdict(float)  # Soma por rota
        self.request_latency_count = defaultdict(int)  # Contagem por rota
        self.request_latency_by_method = defaultdict(lambda: defaultdict(float))  # Soma por rota+método
        self.request_latency_count_by_method = defaultdict(lambda: defaultdict(int))  # Contagem por rota+método
        
        # Métricas de erro
        self.error_count = defaultdict(int)  # Total por rota
        self.error_count_by_type = defaultdict(lambda: defaultdict(int))  # Total por rota+tipo
        
        # Requisições lentas
        self.slow_requests_total = 0
        self.slow_requests_by_route = defaultdict(int)
        
        # Requisições em andamento
        self.requests_in_progress = defaultdict(int)
        self.requests_in_progress_by_method = defaultdict(lambda: defaultdict(int))
        
        # Tamanho de dados transferidos
        self.request_size_sum = defaultdict(int)
        self.request_size_by_method = defaultdict(lambda: defaultdict(int))
        self.response_size_sum = defaultdict(int)
        self.response_size_by_method = defaultdict(lambda: defaultdict(int))
        
        # Métricas de sistema
        self.start_time = time.time()
        self.last_reset_time = time.time()
        
        # Histórico de métricas (para gráficos e tendências)
        self.historical_metrics = []
        self.max_history_entries = 60 * 24 * METRICS_RETENTION_DAYS  # Cada entrada = 1 minuto, por 7 dias
        
        # Lock para operações thread-safe
        self.lock = threading.Lock()
    
    def reset(self):
        """Reinicia todas as métricas, preservando o histórico."""
        with self.lock:
            # Armazenar snapshot atual no histórico
            self._store_snapshot()
            
            # Reiniciar contadores
            self.request_count.clear()
            self.request_count_by_method.clear()
            self.request_count_by_status.clear()
            self.request_latency_sum.clear()
            self.request_latency_count.clear()
            self.request_latency_by_method.clear()
            self.request_latency_count_by_method.clear()
            self.error_count.clear()
            self.error_count_by_type.clear()
            self.slow_requests_total = 0
            self.slow_requests_by_route.clear()
            self.request_size_sum.clear()
            self.request_size_by_method.clear()
            self.response_size_sum.clear()
            self.response_size_by_method.clear()
            
            # Atualizar tempo de último reset
            self.last_reset_time = time.time()
    
    def _store_snapshot(self):
        """Armazena um snapshot das métricas atuais no histórico."""
        now = datetime.now()
        snapshot = {
            "timestamp": now.isoformat(),
            "uptime": time.time() - self.start_time,
            "last_reset_age": time.time() - self.last_reset_time,
            "request_count": dict(self.request_count),
            "error_count": dict(self.error_count),
            "slow_requests": self.slow_requests_total,
            "avg_latency": {
                route: self.request_latency_sum[route] / max(1, self.request_latency_count[route])
                for route in self.request_latency_sum
            }
        }
        
        self.historical_metrics.append(snapshot)
        
        # Limitar o tamanho do histórico
        if len(self.historical_metrics) > self.max_history_entries:
            self.historical_metrics = self.historical_metrics[-self.max_history_entries:]
    
    def to_prometheus(self) -> str:
        """
        Retorna as métricas em formato compatível com Prometheus.
        
        Returns:
            String formatada com as métricas para o Prometheus
        """
        with self.lock:
            metrics = []
            
            # Adicionar metadados
            metrics.append("# HELP ccontrolm_requests_total Total de requisições processadas")
            metrics.append("# TYPE ccontrolm_requests_total counter")
            metrics.append("# HELP ccontrolm_request_duration_seconds Duração das requisições em segundos")
            metrics.append("# TYPE ccontrolm_request_duration_seconds histogram")
            metrics.append("# HELP ccontrolm_errors_total Total de erros por rota")
            metrics.append("# TYPE ccontrolm_errors_total counter")
            metrics.append("# HELP ccontrolm_requests_in_progress Requisições atualmente em processamento")
            metrics.append("# TYPE ccontrolm_requests_in_progress gauge")
            metrics.append("# HELP ccontrolm_slow_requests_total Total de requisições lentas")
            metrics.append("# TYPE ccontrolm_slow_requests_total counter")
            metrics.append("# HELP ccontrolm_request_size_bytes Tamanho das requisições em bytes")
            metrics.append("# TYPE ccontrolm_request_size_bytes counter")
            metrics.append("# HELP ccontrolm_response_size_bytes Tamanho das respostas em bytes")
            metrics.append("# TYPE ccontrolm_response_size_bytes counter")
            metrics.append("# HELP ccontrolm_uptime_seconds Tempo de execução do servidor em segundos")
            metrics.append("# TYPE ccontrolm_uptime_seconds gauge")
            
            # Métricas de uptime
            uptime = time.time() - self.start_time
            metrics.append(f"ccontrolm_uptime_seconds {uptime:.2f}")
            
            # Métricas de contagem de requisições
            for route, count in self.request_count.items():
                metrics.append(f'ccontrolm_requests_total{{route="{route}"}} {count}')
            
            # Métricas de contagem de requisições por método
            for route, methods in self.request_count_by_method.items():
                for method, count in methods.items():
                    metrics.append(f'ccontrolm_requests_total{{route="{route}",method="{method}"}} {count}')
            
            # Métricas de contagem de requisições por status
            for route, statuses in self.request_count_by_status.items():
                for status, count in statuses.items():
                    metrics.append(f'ccontrolm_requests_total{{route="{route}",status="{status}"}} {count}')
            
            # Métricas de latência
            for route in self.request_latency_sum:
                if self.request_latency_count[route] > 0:
                    avg_latency = self.request_latency_sum[route] / self.request_latency_count[route]
                    metrics.append(f'ccontrolm_request_duration_seconds{{route="{route}"}} {avg_latency:.6f}')
            
            # Métricas de latência por método
            for route, methods in self.request_latency_by_method.items():
                for method, latency_sum in methods.items():
                    count = self.request_latency_count_by_method[route][method]
                    if count > 0:
                        avg_latency = latency_sum / count
                        metrics.append(f'ccontrolm_request_duration_seconds{{route="{route}",method="{method}"}} {avg_latency:.6f}')
            
            # Métricas de erros
            for route, count in self.error_count.items():
                metrics.append(f'ccontrolm_errors_total{{route="{route}"}} {count}')
            
            # Métricas de erros por tipo
            for route, error_types in self.error_count_by_type.items():
                for error_type, count in error_types.items():
                    metrics.append(f'ccontrolm_errors_total{{route="{route}",error_type="{error_type}"}} {count}')
            
            # Métricas de requisições em andamento
            for route, count in self.requests_in_progress.items():
                metrics.append(f'ccontrolm_requests_in_progress{{route="{route}"}} {count}')
            
            # Métricas de requisições em andamento por método
            for route, methods in self.requests_in_progress_by_method.items():
                for method, count in methods.items():
                    metrics.append(f'ccontrolm_requests_in_progress{{route="{route}",method="{method}"}} {count}')
            
            # Métricas de requisições lentas
            metrics.append(f'ccontrolm_slow_requests_total {self.slow_requests_total}')
            
            # Métricas de requisições lentas por rota
            for route, count in self.slow_requests_by_route.items():
                metrics.append(f'ccontrolm_slow_requests_total{{route="{route}"}} {count}')
            
            # Métricas de tamanho de requisição
            for route, size in self.request_size_sum.items():
                metrics.append(f'ccontrolm_request_size_bytes{{route="{route}"}} {size}')
            
            # Métricas de tamanho de resposta
            for route, size in self.response_size_sum.items():
                metrics.append(f'ccontrolm_response_size_bytes{{route="{route}"}} {size}')
            
            return "\n".join(metrics)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna as métricas como um dicionário estruturado.
        
        Returns:
            Dicionário com métricas organizadas
        """
        with self.lock:
            # Calcular médias de latência
            latency_avg = {}
            for route in self.request_latency_sum:
                if self.request_latency_count[route] > 0:
                    latency_avg[route] = self.request_latency_sum[route] / self.request_latency_count[route]
            
            # Estruturar as métricas
            return {
                "uptime": time.time() - self.start_time,
                "uptime_formatted": str(timedelta(seconds=int(time.time() - self.start_time))),
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "last_reset": datetime.fromtimestamp(self.last_reset_time).isoformat(),
                "requests": {
                    "total": sum(self.request_count.values()),
                    "by_route": dict(self.request_count),
                    "by_method": {route: dict(methods) for route, methods in self.request_count_by_method.items()},
                    "by_status": {route: dict(statuses) for route, statuses in self.request_count_by_status.items()},
                    "in_progress": dict(self.requests_in_progress),
                    "in_progress_by_method": {route: dict(methods) for route, methods in self.requests_in_progress_by_method.items()},
                },
                "latency": {
                    "average": latency_avg,
                    "by_method": {
                        route: {
                            method: latency_sum / max(1, self.request_latency_count_by_method[route][method])
                            for method, latency_sum in methods.items()
                        }
                        for route, methods in self.request_latency_by_method.items()
                    }
                },
                "errors": {
                    "total": sum(self.error_count.values()),
                    "by_route": dict(self.error_count),
                    "by_type": {route: dict(types) for route, types in self.error_count_by_type.items()}
                },
                "slow_requests": {
                    "total": self.slow_requests_total,
                    "by_route": dict(self.slow_requests_by_route)
                },
                "data_transfer": {
                    "request_size": dict(self.request_size_sum),
                    "response_size": dict(self.response_size_sum)
                },
                "historical": self.historical_metrics[-10:] if self.historical_metrics else []
            }


# Instância global para métricas
metrics = PerfMetrics()


def update_request_count(route: str, method: str, status_code: int) -> None:
    """
    Atualiza contadores de requisições.
    
    Args:
        route: Rota da requisição
        method: Método HTTP
        status_code: Código de status da resposta
    """
    if not ENABLE_METRICS:
        return
        
    with metrics.lock:
        metrics.request_count[route] += 1
        metrics.request_count_by_method[route][method] += 1
        metrics.request_count_by_status[route][status_code] += 1
        
        # Considerar erros (status >= 400)
        if status_code >= 400:
            metrics.error_count[route] += 1


def update_request_latency(route: str, method: str, duration: float) -> None:
    """
    Atualiza métricas de latência de requisições.
    
    Args:
        route: Rota da requisição
        method: Método HTTP
        duration: Duração em segundos
    """
    if not ENABLE_METRICS:
        return
        
    with metrics.lock:
        # Atualizar métricas por rota
        metrics.request_latency_sum[route] += duration
        metrics.request_latency_count[route] += 1
        
        # Atualizar métricas por rota+método
        metrics.request_latency_by_method[route][method] += duration
        metrics.request_latency_count_by_method[route][method] += 1


def update_request_in_progress(route: str, method: str, increment: int) -> None:
    """
    Atualiza contadores de requisições em andamento.
    
    Args:
        route: Rota da requisição
        method: Método HTTP
        increment: Valor a incrementar (1 para início, -1 para fim)
    """
    if not ENABLE_METRICS:
        return
        
    with metrics.lock:
        metrics.requests_in_progress[route] += increment
        metrics.requests_in_progress_by_method[route][method] += increment


def update_error_count(route: str, method: str, error_type: str) -> None:
    """
    Atualiza contadores de erros.
    
    Args:
        route: Rota da requisição
        method: Método HTTP
        error_type: Tipo de erro/exceção
    """
    if not ENABLE_METRICS:
        return
        
    with metrics.lock:
        metrics.error_count[route] += 1
        metrics.error_count_by_type[route][error_type] += 1


def update_request_size(route: str, method: str, size: int) -> None:
    """
    Atualiza métricas de tamanho de requisição.
    
    Args:
        route: Rota da requisição
        method: Método HTTP
        size: Tamanho em bytes
    """
    if not ENABLE_METRICS:
        return
        
    with metrics.lock:
        metrics.request_size_sum[route] += size
        metrics.request_size_by_method[route][method] += size


def update_response_size(route: str, method: str, size: int) -> None:
    """
    Atualiza métricas de tamanho de resposta.
    
    Args:
        route: Rota da requisição
        method: Método HTTP
        size: Tamanho em bytes
    """
    if not ENABLE_METRICS:
        return
        
    with metrics.lock:
        metrics.response_size_sum[route] += size
        metrics.response_size_by_method[route][method] += size


def reset_metrics() -> None:
    """
    Reinicia os contadores de métricas mantendo o histórico.
    
    Esta função é útil para limpar contadores após resolução 
    de problemas ou para iniciar uma nova sessão de monitoramento.
    """
    metrics.reset()


def get_metrics_prometheus() -> str:
    """
    Obtém as métricas formatadas para Prometheus.
    
    Returns:
        String com as métricas no formato Prometheus
    """
    return generate_latest()


def get_metrics_dict() -> Dict[str, Any]:
    """
    Obtém as métricas em formato dict para exibição em API.
    
    Returns:
        Dicionário com métricas para uso em dashboards
    """
    return metrics.to_dict() 