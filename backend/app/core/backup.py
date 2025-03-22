"""
Sistema de backup automático para CCONTROL-M.

Este módulo implementa rotinas de backup para o banco de dados e arquivos
do sistema, com suporte a compressão, criptografia e armazenamento externo.
"""
import os
import sys
import shutil
import datetime
import subprocess
import tarfile
import zipfile
import gzip
import logging
import asyncio
import aiofiles
import aioboto3
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from cryptography.fernet import Fernet
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from app.core.config import settings
from app.utils.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)


class BackupManager:
    """Gerenciador de backups automáticos para banco de dados e arquivos."""
    
    def __init__(
        self,
        backup_dir: str = "backups",
        retention_days: int = 30,
        backup_freq_hours: int = 24,
        encrypt_backups: bool = True,
        compress_backups: bool = True,
        enable_s3_upload: bool = False,
        alert_on_failure: bool = True,
        exclude_paths: List[str] = None,
    ):
        """
        Inicializa o gerenciador de backups.
        
        Args:
            backup_dir: Diretório onde os backups serão armazenados
            retention_days: Número de dias para manter backups antigos
            backup_freq_hours: Frequência de backups em horas
            encrypt_backups: Se True, criptografa os backups
            compress_backups: Se True, comprime os backups
            enable_s3_upload: Se True, envia backups para o Amazon S3
            alert_on_failure: Se True, envia alertas quando backups falham
            exclude_paths: Lista de caminhos a serem excluídos do backup
        """
        self.backup_dir = os.path.abspath(backup_dir)
        self.retention_days = retention_days
        self.backup_freq_hours = backup_freq_hours
        self.encrypt_backups = encrypt_backups
        self.compress_backups = compress_backups
        self.enable_s3_upload = enable_s3_upload
        self.alert_on_failure = alert_on_failure
        self.exclude_paths = exclude_paths or []
        
        # Diretórios específicos para diferentes tipos de backup
        self.db_backup_dir = os.path.join(self.backup_dir, "database")
        self.files_backup_dir = os.path.join(self.backup_dir, "files")
        self.logs_backup_dir = os.path.join(self.backup_dir, "logs")
        
        # Garantir que os diretórios existam
        self._create_backup_dirs()
        
        # Inicializar gerador de chaves para criptografia
        if self.encrypt_backups:
            self._setup_encryption()
        
        # Métricas de backup
        self.last_backup_time = None
        self.last_backup_size = 0
        self.last_backup_status = "not_started"
        self.backup_count = 0
        self.backup_failures = 0
    
    def _create_backup_dirs(self) -> None:
        """Cria os diretórios necessários para os backups."""
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.db_backup_dir, exist_ok=True)
        os.makedirs(self.files_backup_dir, exist_ok=True)
        os.makedirs(self.logs_backup_dir, exist_ok=True)
        logger.info(f"Diretórios de backup criados em: {self.backup_dir}")
    
    def _setup_encryption(self) -> None:
        """Configura a criptografia para backups."""
        key_path = os.path.join(self.backup_dir, ".backup_key")
        
        # Se já existir uma chave, carregá-la, senão gerar nova
        if os.path.exists(key_path):
            try:
                with open(key_path, "rb") as key_file:
                    self.encryption_key = key_file.read()
                logger.info("Chave de criptografia de backup carregada")
            except Exception as e:
                logger.error(f"Erro ao carregar chave de criptografia: {str(e)}")
                self.encryption_key = Fernet.generate_key()
                self._save_encryption_key(key_path)
        else:
            self.encryption_key = Fernet.generate_key()
            self._save_encryption_key(key_path)
        
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _save_encryption_key(self, key_path: str) -> None:
        """Salva a chave de criptografia em arquivo seguro."""
        try:
            # Definir permissões restritas antes de criar o arquivo
            with open(key_path, "wb") as key_file:
                key_file.write(self.encryption_key)
            
            # Ajustar permissões para que apenas o proprietário possa ler
            os.chmod(key_path, 0o600)
            logger.info("Nova chave de criptografia de backup gerada e armazenada")
        except Exception as e:
            logger.error(f"Erro ao salvar chave de criptografia: {str(e)}")
    
    async def run_backup_scheduler(self) -> None:
        """Inicia o agendador de backups periódicos."""
        logger.info(f"Iniciando agendador de backups a cada {self.backup_freq_hours} horas")
        while True:
            try:
                await self.perform_full_backup()
                await self.clean_old_backups()
                
                # Aguardar até o próximo backup
                interval_seconds = self.backup_freq_hours * 3600
                logger.info(f"Próximo backup programado em {self.backup_freq_hours} horas")
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Erro no agendador de backups: {str(e)}")
                if self.alert_on_failure:
                    await self.send_backup_alert(f"Erro no agendador de backups: {str(e)}")
                # Aguardar um tempo menor para tentar novamente em caso de falha
                await asyncio.sleep(3600)  # 1 hora
    
    async def perform_full_backup(self) -> bool:
        """
        Realiza um backup completo do sistema.
        
        Returns:
            True se o backup foi bem-sucedido, False caso contrário
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}"
        logger.info(f"Iniciando backup completo: {backup_id}")
        
        try:
            self.last_backup_status = "in_progress"
            self.last_backup_time = datetime.datetime.now()
            
            # Backup do banco de dados
            db_success = await self.backup_database(backup_id)
            
            # Backup dos arquivos
            files_success = await self.backup_files(backup_id)
            
            # Backup dos logs
            logs_success = await self.backup_logs(backup_id)
            
            if db_success and files_success and logs_success:
                self.last_backup_status = "success"
                self.backup_count += 1
                logger.info(f"Backup completo finalizado com sucesso: {backup_id}")
                return True
            else:
                self.last_backup_status = "partial_failure"
                self.backup_failures += 1
                error_message = f"Backup parcial {backup_id}: DB={db_success}, Files={files_success}, Logs={logs_success}"
                logger.warning(error_message)
                if self.alert_on_failure:
                    await self.send_backup_alert(error_message)
                return False
        except Exception as e:
            self.last_backup_status = "failure"
            self.backup_failures += 1
            error_message = f"Falha no backup {backup_id}: {str(e)}"
            logger.error(error_message)
            if self.alert_on_failure:
                await self.send_backup_alert(error_message)
            return False
    
    async def backup_database(self, backup_id: str) -> bool:
        """
        Realiza backup do banco de dados.
        
        Args:
            backup_id: Identificador único do backup
            
        Returns:
            True se o backup do banco foi bem-sucedido, False caso contrário
        """
        try:
            db_filename = f"{backup_id}_database.sql"
            db_filepath = os.path.join(self.db_backup_dir, db_filename)
            
            # Determinar as credenciais do banco de dados a partir das configurações
            db_host = settings.POSTGRES_SERVER
            db_port = settings.POSTGRES_PORT
            db_name = settings.POSTGRES_DB
            db_user = settings.POSTGRES_USER
            db_password = settings.POSTGRES_PASSWORD
            
            # Executar pg_dump para realizar o backup
            command = [
                "pg_dump",
                f"--host={db_host}",
                f"--port={db_port}",
                f"--username={db_user}",
                f"--dbname={db_name}",
                "--format=plain",
                f"--file={db_filepath}"
            ]
            
            # Configurar variável de ambiente PGPASSWORD
            env = os.environ.copy()
            env["PGPASSWORD"] = db_password
            
            # Executar comando de backup
            process = await asyncio.create_subprocess_exec(
                *command,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Erro ao realizar backup do banco: {stderr.decode()}")
                return False
            
            backup_size = os.path.getsize(db_filepath)
            logger.info(f"Backup do banco concluído: {db_filepath} ({backup_size} bytes)")
            
            # Comprimir e/ou criptografar o arquivo
            processed_filepath = await self._process_backup_file(db_filepath)
            
            # Enviar para armazenamento externo se configurado
            if self.enable_s3_upload:
                await self._upload_to_s3(processed_filepath, "database")
            
            return True
        except Exception as e:
            logger.error(f"Erro durante backup do banco de dados: {str(e)}")
            return False
    
    async def backup_files(self, backup_id: str) -> bool:
        """
        Realiza backup dos arquivos da aplicação.
        
        Args:
            backup_id: Identificador único do backup
            
        Returns:
            True se o backup dos arquivos foi bem-sucedido, False caso contrário
        """
        try:
            files_filename = f"{backup_id}_files.tar"
            files_filepath = os.path.join(self.files_backup_dir, files_filename)
            
            # Diretórios a serem incluídos no backup
            source_dirs = [
                "uploads",  # Arquivos enviados pelos usuários
                "reports",  # Relatórios gerados
                "static",   # Arquivos estáticos
            ]
            
            # Criar arquivo tar
            with tarfile.open(files_filepath, "w") as tar:
                for directory in source_dirs:
                    dir_path = os.path.join(settings.PROJECT_ROOT, directory)
                    if os.path.exists(dir_path):
                        tar.add(
                            dir_path, 
                            arcname=os.path.basename(dir_path),
                            filter=self._filter_backup_files
                        )
            
            backup_size = os.path.getsize(files_filepath)
            logger.info(f"Backup de arquivos concluído: {files_filepath} ({backup_size} bytes)")
            
            # Comprimir e/ou criptografar o arquivo
            processed_filepath = await self._process_backup_file(files_filepath)
            
            # Enviar para armazenamento externo se configurado
            if self.enable_s3_upload:
                await self._upload_to_s3(processed_filepath, "files")
            
            return True
        except Exception as e:
            logger.error(f"Erro durante backup de arquivos: {str(e)}")
            return False
    
    def _filter_backup_files(self, tarinfo: tarfile.TarInfo) -> Optional[tarfile.TarInfo]:
        """
        Filtra arquivos a serem incluídos no backup.
        
        Args:
            tarinfo: Informações do arquivo a ser avaliado
            
        Returns:
            TarInfo se o arquivo deve ser incluído, None se deve ser excluído
        """
        # Verificar se o caminho deve ser excluído
        for exclude_path in self.exclude_paths:
            if exclude_path in tarinfo.name:
                return None
        
        # Excluir arquivos temporários, caches e outros desnecessários
        exclude_patterns = [
            "__pycache__",
            ".git",
            ".idea",
            ".vscode",
            ".env",
            ".DS_Store",
            "node_modules",
            ".tmp",
            ".temp",
            ".cache",
            ".pytest_cache",
        ]
        
        for pattern in exclude_patterns:
            if pattern in tarinfo.name:
                return None
        
        # Remover permissões não essenciais para segurança
        tarinfo.mode = 0o644  # Permissões padrão para arquivos
        
        return tarinfo
    
    async def backup_logs(self, backup_id: str) -> bool:
        """
        Realiza backup dos arquivos de log.
        
        Args:
            backup_id: Identificador único do backup
            
        Returns:
            True se o backup dos logs foi bem-sucedido, False caso contrário
        """
        try:
            logs_filename = f"{backup_id}_logs.tar"
            logs_filepath = os.path.join(self.logs_backup_dir, logs_filename)
            
            # Diretório de logs
            logs_dir = os.path.join(settings.PROJECT_ROOT, "logs")
            
            if not os.path.exists(logs_dir):
                logger.warning(f"Diretório de logs não encontrado: {logs_dir}")
                return True  # Não falhar se o diretório não existir
            
            # Criar arquivo tar
            with tarfile.open(logs_filepath, "w") as tar:
                tar.add(logs_dir, arcname=os.path.basename(logs_dir))
            
            backup_size = os.path.getsize(logs_filepath)
            logger.info(f"Backup de logs concluído: {logs_filepath} ({backup_size} bytes)")
            
            # Comprimir e/ou criptografar o arquivo
            processed_filepath = await self._process_backup_file(logs_filepath)
            
            # Enviar para armazenamento externo se configurado
            if self.enable_s3_upload:
                await self._upload_to_s3(processed_filepath, "logs")
            
            return True
        except Exception as e:
            logger.error(f"Erro durante backup de logs: {str(e)}")
            return False
    
    async def _process_backup_file(self, filepath: str) -> str:
        """
        Processa um arquivo de backup (compressão/criptografia).
        
        Args:
            filepath: Caminho do arquivo a ser processado
            
        Returns:
            Caminho do arquivo processado
        """
        processed_path = filepath
        
        # Compressão
        if self.compress_backups:
            compressed_path = f"{filepath}.gz"
            await self._compress_file(filepath, compressed_path)
            processed_path = compressed_path
            
            # Remover arquivo original após compressão
            os.remove(filepath)
        
        # Criptografia
        if self.encrypt_backups:
            encrypted_path = f"{processed_path}.enc"
            await self._encrypt_file(processed_path, encrypted_path)
            processed_path = encrypted_path
            
            # Remover arquivo intermediário após criptografia
            if processed_path != filepath:
                os.remove(processed_path)
        
        return processed_path
    
    async def _compress_file(self, source_path: str, target_path: str) -> None:
        """
        Comprime um arquivo usando gzip.
        
        Args:
            source_path: Caminho do arquivo de origem
            target_path: Caminho do arquivo comprimido
        """
        try:
            # Usar asyncio para não bloquear durante a compressão
            loop = asyncio.get_event_loop()
            
            # Compressão em segundo plano
            await loop.run_in_executor(
                None,
                self._compress_file_sync,
                source_path,
                target_path
            )
            
            logger.info(f"Arquivo comprimido: {target_path}")
        except Exception as e:
            logger.error(f"Erro ao comprimir arquivo {source_path}: {str(e)}")
            raise
    
    def _compress_file_sync(self, source_path: str, target_path: str) -> None:
        """
        Versão síncrona da compressão de arquivo para uso com run_in_executor.
        
        Args:
            source_path: Caminho do arquivo de origem
            target_path: Caminho do arquivo comprimido
        """
        with open(source_path, 'rb') as f_in:
            with gzip.open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    async def _encrypt_file(self, source_path: str, target_path: str) -> None:
        """
        Criptografa um arquivo.
        
        Args:
            source_path: Caminho do arquivo de origem
            target_path: Caminho do arquivo criptografado
        """
        try:
            # Ler arquivo a ser criptografado
            async with aiofiles.open(source_path, 'rb') as file:
                data = await file.read()
            
            # Criptografar dados
            encrypted_data = self.cipher_suite.encrypt(data)
            
            # Escrever arquivo criptografado
            async with aiofiles.open(target_path, 'wb') as file:
                await file.write(encrypted_data)
            
            logger.info(f"Arquivo criptografado: {target_path}")
        except Exception as e:
            logger.error(f"Erro ao criptografar arquivo {source_path}: {str(e)}")
            raise
    
    async def _decrypt_file(self, source_path: str, target_path: str) -> None:
        """
        Descriptografa um arquivo.
        
        Args:
            source_path: Caminho do arquivo criptografado
            target_path: Caminho do arquivo descriptografado
        """
        try:
            # Ler arquivo criptografado
            async with aiofiles.open(source_path, 'rb') as file:
                encrypted_data = await file.read()
            
            # Descriptografar dados
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            # Escrever arquivo descriptografado
            async with aiofiles.open(target_path, 'wb') as file:
                await file.write(decrypted_data)
            
            logger.info(f"Arquivo descriptografado: {target_path}")
        except Exception as e:
            logger.error(f"Erro ao descriptografar arquivo {source_path}: {str(e)}")
            raise
    
    async def _upload_to_s3(self, filepath: str, category: str) -> None:
        """
        Envia um arquivo para o Amazon S3.
        
        Args:
            filepath: Caminho do arquivo a ser enviado
            category: Categoria do backup (database, files, logs)
        """
        try:
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                logger.warning("Credenciais AWS não configuradas. Upload para S3 ignorado.")
                return
            
            bucket_name = settings.AWS_BACKUP_BUCKET
            if not bucket_name:
                logger.warning("Nome do bucket AWS não configurado. Upload para S3 ignorado.")
                return
            
            # Nome do arquivo sem o caminho
            filename = os.path.basename(filepath)
            
            # Definir caminho no S3 (incluindo a categoria e data)
            today = datetime.datetime.now().strftime("%Y/%m/%d")
            s3_key = f"backups/{category}/{today}/{filename}"
            
            # Criar sessão S3
            session = aioboto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            async with session.client('s3') as s3:
                # Upload do arquivo
                async with aiofiles.open(filepath, 'rb') as data:
                    await s3.upload_fileobj(
                        data,
                        bucket_name,
                        s3_key
                    )
            
            logger.info(f"Arquivo enviado para S3: s3://{bucket_name}/{s3_key}")
        except Exception as e:
            logger.error(f"Erro ao enviar arquivo para S3 {filepath}: {str(e)}")
            raise
    
    async def clean_old_backups(self) -> None:
        """Remove backups antigos de acordo com a política de retenção."""
        try:
            logger.info(f"Iniciando limpeza de backups antigos (retenção: {self.retention_days} dias)")
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
            
            # Backups locais
            await self._clean_local_backups(self.db_backup_dir, cutoff_date)
            await self._clean_local_backups(self.files_backup_dir, cutoff_date)
            await self._clean_local_backups(self.logs_backup_dir, cutoff_date)
            
            # Backups no S3
            if self.enable_s3_upload:
                await self._clean_s3_backups(cutoff_date)
            
            logger.info("Limpeza de backups antigos concluída")
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {str(e)}")
    
    async def _clean_local_backups(self, directory: str, cutoff_date: datetime.datetime) -> None:
        """
        Remove arquivos de backup antigos de um diretório local.
        
        Args:
            directory: Diretório a ser limpo
            cutoff_date: Data de corte para remoção
        """
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Ignorar diretórios
            if os.path.isdir(file_path):
                continue
            
            # Verificar data de modificação
            file_mod_time = datetime.datetime.fromtimestamp(
                os.path.getmtime(file_path)
            )
            
            if file_mod_time < cutoff_date:
                try:
                    os.remove(file_path)
                    logger.info(f"Backup antigo removido: {file_path}")
                except Exception as e:
                    logger.error(f"Erro ao remover backup antigo {file_path}: {str(e)}")
    
    async def _clean_s3_backups(self, cutoff_date: datetime.datetime) -> None:
        """
        Remove arquivos de backup antigos do Amazon S3.
        
        Args:
            cutoff_date: Data de corte para remoção
        """
        try:
            bucket_name = settings.AWS_BACKUP_BUCKET
            
            # Criar sessão S3
            session = aioboto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            async with session.client('s3') as s3:
                # Listar objetos no bucket
                paginator = s3.get_paginator('list_objects_v2')
                
                # Prefixo para backups
                prefix = "backups/"
                
                count_deleted = 0
                async for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                    if 'Contents' not in page:
                        continue
                    
                    for obj in page['Contents']:
                        # Verificar data de modificação
                        if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                            await s3.delete_object(
                                Bucket=bucket_name,
                                Key=obj['Key']
                            )
                            count_deleted += 1
                            
                            if count_deleted % 100 == 0:
                                logger.info(f"Removidos {count_deleted} backups antigos do S3")
                
                if count_deleted > 0:
                    logger.info(f"Total de {count_deleted} backups antigos removidos do S3")
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos do S3: {str(e)}")
    
    async def send_backup_alert(self, message: str) -> None:
        """
        Envia alerta sobre falha no backup.
        
        Args:
            message: Mensagem de alerta
        """
        if not settings.SMTP_SERVER or not settings.SMTP_PORT:
            logger.warning("Servidor SMTP não configurado. Alerta de backup não enviado.")
            return
        
        try:
            # Configurar email
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_SENDER
            msg['To'] = settings.ADMIN_EMAIL
            msg['Subject'] = f"ALERTA DE BACKUP - CCONTROL-M - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Corpo do email
            body = f"""
            <html>
            <body>
                <h2>Alerta de Backup - CCONTROL-M</h2>
                <p><strong>Data/Hora:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Ambiente:</strong> {settings.APP_ENV}</p>
                <p><strong>Mensagem:</strong> {message}</p>
                <p>Por favor, verifique o sistema de backup o quanto antes.</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            # Conectar ao servidor SMTP
            smtp = aiosmtplib.SMTP(
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT,
                use_tls=settings.SMTP_USE_TLS
            )
            
            await smtp.connect()
            
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            # Enviar email
            await smtp.send_message(msg)
            await smtp.quit()
            
            logger.info(f"Alerta de backup enviado para {settings.ADMIN_EMAIL}")
        except Exception as e:
            logger.error(f"Erro ao enviar alerta de backup: {str(e)}")

# Função para iniciar o agendador de backups
async def start_backup_scheduler() -> None:
    """Inicia o agendador de backups automáticos."""
    backup_manager = BackupManager(
        backup_dir=os.path.join(settings.PROJECT_ROOT, "backups"),
        retention_days=settings.BACKUP_RETENTION_DAYS,
        backup_freq_hours=settings.BACKUP_FREQUENCY_HOURS,
        encrypt_backups=settings.ENCRYPT_BACKUPS,
        compress_backups=True,
        enable_s3_upload=settings.ENABLE_S3_BACKUP,
        alert_on_failure=True
    )
    
    await backup_manager.run_backup_scheduler()


# Função para realizar um backup manual
async def perform_manual_backup() -> bool:
    """
    Realiza um backup manual do sistema.
    
    Returns:
        True se o backup foi bem-sucedido, False caso contrário
    """
    backup_manager = BackupManager(
        backup_dir=os.path.join(settings.PROJECT_ROOT, "backups"),
        retention_days=settings.BACKUP_RETENTION_DAYS,
        encrypt_backups=settings.ENCRYPT_BACKUPS,
        compress_backups=True,
        enable_s3_upload=settings.ENABLE_S3_BACKUP,
        alert_on_failure=True
    )
    
    return await backup_manager.perform_full_backup() 