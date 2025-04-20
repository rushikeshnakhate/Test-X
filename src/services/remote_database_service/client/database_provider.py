"""
Remote database provider implementation.
"""
from typing import Type, Optional

from src.base_classes.base_connection import BaseConnection
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.common.logging_config import setup_logging
from src.services.remote_database_service.client.database_client import DatabaseClient

# Setup logging for database provider
logger = setup_logging("database_provider", "DEBUG")


class RemoteDatabaseProvider(BaseConnectionProvider):
    """Provider for remote database connections"""

    def __init__(self):
        """Initialize the database provider."""
        logger.info("Initializing RemoteDatabaseProvider")
        super().__init__()
        logger.debug("Database provider initialized")

    async def load_config(self) -> None:
        """Load RemoteDatabase-specific configuration"""
        logger.debug("Loading RemoteDatabase configuration")
        try:
            # Get configuration from config loader
            all_configs = self._config_loader.get_all_configs()
            if not all_configs or 'config' not in all_configs:
                logger.warning("No configuration found in config loader")
                return

            # Extract RemoteDatabase configuration from the nested config structure
            cfg = all_configs['config'].get('remote_database')
            if not cfg:
                logger.warning(
                    f"No RemoteDatabase configuration found in config, available services: {list(all_configs['config'].keys())}")
                return

            # Extract RemoteDatabase configuration
            if cfg.get('enable', True):
                connections = cfg.get('connections', [])
                for conn in connections:
                    if conn.get('enable', True):
                        connection_id = conn.get('name', 'default')
                        self._enabled_connections.append(connection_id)
                        self._config[connection_id] = conn
                logger.info("RemoteDatabase configuration loaded successfully")
                logger.debug(f"Enabled connections: {self._enabled_connections}")
            else:
                logger.info("RemoteDatabase provider is disabled in configuration")
        except Exception as e:
            logger.error(f"Error loading RemoteDatabase configuration: {str(e)}", exc_info=True)
            raise

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the RemoteDatabase connection class"""
        return DatabaseClient

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new RemoteDatabase connection"""
        logger.debug(f"Creating RemoteDatabase connection for ID: {connection_id}")

        try:
            if connection_id not in self._config:
                logger.warning(f"No configuration found for connection ID: {connection_id}")
                return None

            config = self._config[connection_id]
            connection = DatabaseClient(config)
            await connection.connect()
            logger.info(f"RemoteDatabase connection created successfully for ID: {connection_id}")
            return connection
        except Exception as e:
            logger.error(f"Error creating RemoteDatabase connection: {str(e)}", exc_info=True)
            return None
