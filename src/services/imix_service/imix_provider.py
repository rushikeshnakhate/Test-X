"""IMIX provider implementation"""

from typing import Dict, Any, Type, Optional, List
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.base_classes.base_connection import BaseConnection

from src.common.logging_config import setup_logging, get_logger
from src.services.imix_service.imix_service import IMIXConnection

# Setup logging for IMIX provider
logger = setup_logging("imix_provider", "DEBUG")


class IMIXProvider(BaseConnectionProvider):
    """Provider for IMIX connections"""

    def __init__(self):
        """Initialize the IMIX provider."""
        logger.info("Initializing IMIXProvider")
        super().__init__()
        logger.debug("IMIX provider initialized")

    async def load_config(self) -> None:
        """Load IMIX-specific configuration"""
        logger.debug("Loading IMIX configuration")
        try:
            # Get configuration from config loader
            all_configs = self._config_loader.get_all_configs()
            if not all_configs or 'config' not in all_configs:
                logger.warning("No configuration found in config loader")
                return

            # Extract IMIX configuration from the nested config structure
            cfg = all_configs['config'].get('imix')
            if not cfg:
                logger.warning(
                    f"No IMIX configuration found in config, available services: {list(all_configs['config'].keys())}")
                return

            # Extract IMIX configuration
            if cfg.get('enable', True):
                connections = cfg.get('connections', [])
                for conn in connections:
                    if conn.get('enable', True):
                        connection_id = conn.get('name', 'default')
                        self._enabled_connections.append(connection_id)
                        self._config[connection_id] = conn
                logger.info("IMIX configuration loaded successfully")
                logger.debug(f"Enabled connections: {self._enabled_connections}")
            else:
                logger.info("IMIX provider is disabled in configuration")
        except Exception as e:
            logger.error(f"Error loading IMIX configuration: {str(e)}", exc_info=True)
            raise

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the IMIX connection class"""
        return IMIXConnection

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new IMIX connection"""
        logger.debug(f"Creating IMIX connection for ID: {connection_id}")
        try:
            if connection_id not in self._config:
                logger.warning(f"No configuration found for connection ID: {connection_id}")
                return None

            config = self._config[connection_id]
            connection = IMIXConnection(config)
            await connection.connect()
            logger.info(f"IMIX connection created successfully for ID: {connection_id}")
            return connection
        except Exception as e:
            logger.error(f"Error creating IMIX connection: {str(e)}", exc_info=True)
            return None
