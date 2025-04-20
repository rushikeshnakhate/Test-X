"""Command provider implementation"""

from typing import Dict, Any, Type, Optional

from src.base_classes.base_connection import BaseConnection
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.common.logging_config import setup_logging
from src.services.remote_command_service.client import RemoteCommandConnection

# Setup logging for command provider
logger = setup_logging("command_provider", "DEBUG")


class RemoteCommandProvider(BaseConnectionProvider):
    """Provider for remote command execution"""

    def __init__(self):
        """Initialize the command provider."""
        logger.info("Initializing RemoteCommandProvider")
        super().__init__()
        logger.debug("Command provider initialized")

    async def load_config(self) -> None:
        """Load command-specific configuration"""
        logger.debug("Loading command configuration")
        try:
            # Get configuration from config loader
            all_configs = self._config_loader.get_all_configs()
            if not all_configs or 'config' not in all_configs:
                logger.warning("No configuration found in config loader")
                return

            # Extract command configuration from the nested config structure
            cfg = all_configs['config'].get('command')
            if not cfg:
                logger.warning(
                    f"No command configuration found in config, available services: {list(all_configs['config'].keys())}")
                return

            # Extract command configuration
            if cfg.get('enable', True):
                connections = cfg.get('connections', [])
                for conn in connections:
                    if conn.get('enable', True):
                        connection_id = conn.get('name', 'default')
                        self._enabled_connections.append(connection_id)
                        self._config[connection_id] = conn
                logger.info("Command configuration loaded successfully")
                logger.debug(f"Enabled connections: {self._enabled_connections}")
            else:
                logger.info("Command provider is disabled in configuration")
        except Exception as e:
            logger.error(f"Error loading command configuration: {str(e)}", exc_info=True)
            raise

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the command connection class"""
        return RemoteCommandConnection

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new command connection"""
        logger.debug(f"Creating command connection for ID: {connection_id}")
        try:
            if connection_id not in self._config:
                logger.warning(f"No configuration found for connection ID: {connection_id}")
                return None

            config = self._config[connection_id]
            connection = RemoteCommandConnection(config)
            await connection.connect()
            logger.info(f"Command connection created successfully for ID: {connection_id}")
            return connection
        except Exception as e:
            logger.error(f"Error creating command connection: {str(e)}", exc_info=True)
            return None
