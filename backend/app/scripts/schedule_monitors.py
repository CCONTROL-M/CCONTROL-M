"""
Script para agendamento de tarefas de monitoramento da aplicação CCONTROL-M.
Este módulo implementa um mecanismo de agendamento de tarefas periódicas
para monitoramento do sistema, incluindo:
- Coleta de métricas de desempenho
- Verificação de uso de recursos
- Limpeza de dados temporários
"""

import threading
import time
import logging
import asyncio
import os
import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional

# Importar utilitários
from app.utils.logging_config import get_logger
from app.config.settings import settings

# Configuração de logger
logger = get_logger(__name__)

# Variável para controlar se o agendador está ativo
scheduler_running = False
scheduler_thread = None

# Lista de tarefas agendadas
scheduled_tasks = []


class ScheduledTask:
    """Classe para representar uma tarefa agendada"""
    
    def __init__(
        self,
        name: str,
        interval_seconds: int,
        task_func: Callable,
        is_async: bool = False,
        enabled: bool = True,
        description: str = ""
    ):
        """
        Inicializa uma tarefa agendada
        
        Args:
            name: Nome da tarefa
            interval_seconds: Intervalo de execução em segundos
            task_func: Função a ser executada
            is_async: Se a função é assíncrona
            enabled: Se a tarefa está habilitada
            description: Descrição da tarefa
        """
        self.name = name
        self.interval_seconds = interval_seconds
        self.task_func = task_func
        self.is_async = is_async
        self.enabled = enabled
        self.description = description
        self.last_run = None
        self.next_run = datetime.now() + timedelta(seconds=interval_seconds)
        self.running = False
        self.error_count = 0
        self.success_count = 0


def register_task(
    name: str,
    interval_seconds: int,
    task_func: Callable,
    is_async: bool = False,
    enabled: bool = True,
    description: str = ""
) -> ScheduledTask:
    """
    Registra uma nova tarefa no agendador
    
    Args:
        name: Nome da tarefa
        interval_seconds: Intervalo de execução em segundos
        task_func: Função a ser executada
        is_async: Se a função é assíncrona
        enabled: Se a tarefa está habilitada
        description: Descrição da tarefa
    
    Returns:
        ScheduledTask: A tarefa registrada
    """
    task = ScheduledTask(
        name=name,
        interval_seconds=interval_seconds,
        task_func=task_func,
        is_async=is_async,
        enabled=enabled,
        description=description
    )
    
    scheduled_tasks.append(task)
    logger.info(f"Tarefa '{name}' registrada com intervalo de {interval_seconds} segundos")
    return task


async def collect_system_metrics():
    """Coleta métricas do sistema e registra"""
    try:
        # Coletar informações de memória
        memory = psutil.virtual_memory()
        
        # Coletar informações de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Coletar informações de disco
        disk = psutil.disk_usage('/')
        
        # Registrar no log
        logger.info(
            f"Métricas do sistema - "
            f"CPU: {cpu_percent}%, "
            f"Memória: {memory.percent}% (usado: {memory.used / (1024 * 1024):.1f}MB), "
            f"Disco: {disk.percent}% (livre: {disk.free / (1024 * 1024 * 1024):.1f}GB)"
        )
        
        # Caso o uso seja alto, registrar um alerta
        if cpu_percent > 80:
            logger.warning(f"Uso de CPU elevado: {cpu_percent}%")
        
        if memory.percent > 80:
            logger.warning(f"Uso de memória elevado: {memory.percent}%")
        
        if disk.percent > 80:
            logger.warning(f"Espaço em disco baixo: {disk.free / (1024 * 1024 * 1024):.1f}GB livre")
            
    except Exception as e:
        logger.error(f"Erro ao coletar métricas do sistema: {str(e)}")


async def clean_temp_files():
    """Limpa arquivos temporários antigos"""
    try:
        # Diretório de uploads temporários
        temp_dir = os.path.join(settings.UPLOAD_DIR, "temp")
        
        # Verificar se o diretório existe
        if not os.path.exists(temp_dir):
            return
        
        # Obter data limite (arquivos mais antigos que 1 dia)
        limit_date = datetime.now() - timedelta(days=1)
        count = 0
        
        # Listar arquivos no diretório
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            
            # Verificar se é um arquivo
            if os.path.isfile(file_path):
                # Obter data de criação/modificação
                file_time = os.path.getmtime(file_path)
                file_date = datetime.fromtimestamp(file_time)
                
                # Remover se for mais antigo que o limite
                if file_date < limit_date:
                    os.remove(file_path)
                    count += 1
        
        if count > 0:
            logger.info(f"Limpeza de arquivos temporários: {count} arquivos removidos")
            
    except Exception as e:
        logger.error(f"Erro ao limpar arquivos temporários: {str(e)}")


def scheduler_loop():
    """Loop principal do agendador de tarefas"""
    global scheduler_running
    
    # Criar event loop assíncrono para a thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    logger.info("Iniciando loop do agendador de tarefas")
    
    try:
        while scheduler_running:
            now = datetime.now()
            
            # Verificar todas as tarefas registradas
            for task in scheduled_tasks:
                if task.enabled and not task.running and now >= task.next_run:
                    # Marcar como em execução
                    task.running = True
                    task.last_run = now
                    task.next_run = now + timedelta(seconds=task.interval_seconds)
                    
                    try:
                        if task.is_async:
                            # Executar tarefa assíncrona
                            loop.run_until_complete(task.task_func())
                        else:
                            # Executar tarefa síncrona
                            task.task_func()
                            
                        task.success_count += 1
                        logger.debug(f"Tarefa '{task.name}' executada com sucesso")
                    except Exception as e:
                        task.error_count += 1
                        logger.error(f"Erro ao executar tarefa '{task.name}': {str(e)}")
                    finally:
                        # Marcar como concluída
                        task.running = False
            
            # Aguardar um intervalo curto
            time.sleep(1)
    except Exception as e:
        logger.error(f"Erro no loop do agendador: {str(e)}")
    finally:
        # Fechar o loop assíncrono
        loop.close()
        logger.info("Loop do agendador de tarefas encerrado")


def start_scheduler_thread() -> threading.Thread:
    """
    Inicia a thread do agendador de tarefas
    
    Returns:
        Thread do agendador
    """
    global scheduler_running, scheduler_thread
    
    # Verificar se já está rodando
    if scheduler_running:
        logger.warning("O agendador de tarefas já está em execução")
        return scheduler_thread
    
    # Configurar tarefas padrão
    if settings.ENABLE_MONITORING and not scheduled_tasks:
        # Registrar tarefas de monitoramento
        register_task(
            name="system_metrics",
            interval_seconds=settings.COLLECT_METRICS_INTERVAL,
            task_func=collect_system_metrics,
            is_async=True,
            description="Coleta métricas do sistema (CPU, memória, disco)"
        )
        
        # Limpeza de arquivos temporários (a cada 6 horas)
        register_task(
            name="clean_temp_files",
            interval_seconds=6 * 60 * 60,
            task_func=clean_temp_files,
            is_async=True,
            description="Limpa arquivos temporários antigos"
        )
    
    # Marcar como em execução
    scheduler_running = True
    
    # Iniciar thread
    scheduler_thread = threading.Thread(
        target=scheduler_loop,
        name="scheduler-thread",
        daemon=True
    )
    
    scheduler_thread.start()
    logger.info("Thread do agendador de tarefas iniciada")
    
    return scheduler_thread


def stop_scheduler_thread():
    """Para a thread do agendador de tarefas"""
    global scheduler_running
    
    if not scheduler_running:
        logger.warning("O agendador de tarefas não está em execução")
        return
    
    # Marcar para parar
    scheduler_running = False
    logger.info("Thread do agendador de tarefas marcada para encerramento")


def get_tasks_status() -> List[Dict[str, Any]]:
    """
    Obtém o status de todas as tarefas registradas
    
    Returns:
        Lista com o status de cada tarefa
    """
    result = []
    
    for task in scheduled_tasks:
        result.append({
            "name": task.name,
            "description": task.description,
            "enabled": task.enabled,
            "interval_seconds": task.interval_seconds,
            "last_run": task.last_run.isoformat() if task.last_run else None,
            "next_run": task.next_run.isoformat() if task.next_run else None,
            "running": task.running,
            "success_count": task.success_count,
            "error_count": task.error_count
        })
    
    return result 