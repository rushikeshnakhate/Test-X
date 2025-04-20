"""Oracle provider implementation"""

from typing import Dict, Any, Type, Optional, List
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.base_classes.base_connection import BaseConnection

from src.common.logging_config import setup_logging, get_logger
from src.services.oracle.oracle_service import OracleConnection

# Setup logging for Oracle provider
logger = setup_logging("oracle_provider", "DEBUG")


class OracleProvider(BaseConnectionProvider):
    """Provider for Oracle connections"""

    def __init__(self):
        """Initialize the Oracle provider."""
        logger.info("Initializing OracleProvider")
        super().__init__()
        logger.debug("Oracle provider initialized")

    async def load_config(self) -> None:
        """Load Oracle-specific configuration"""
        logger.debug("Loading Oracle configuration")
        try:
            # Get configuration from config loader
            all_configs = self._config_loader.get_all_configs()
            if not all_configs or 'config' not in all_configs:
                logger.warning("No configuration found in config loader")
                return

            # Extract Oracle configuration from the nested config structure
            cfg = all_configs['config'].get('oracle')
            if not cfg:
                logger.warning(
                    f"No Oracle configuration found in config, available services: {list(all_configs['config'].keys())}")
                return

            # Extract Oracle configuration
            if cfg.get('enable', True):
                connections = cfg.get('connections', [])
                for conn in connections:
                    if conn.get('enable', True):
                        connection_id = conn.get('name', 'default')
                        self._enabled_connections.append(connection_id)
                        self._config[connection_id] = conn
                logger.info("Oracle configuration loaded successfully")
                logger.debug(f"Enabled connections: {self._enabled_connections}")
            else:
                logger.info("Oracle provider is disabled in configuration")
        except Exception as e:
            logger.error(f"Error loading Oracle configuration: {str(e)}", exc_info=True)
            raise

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the Oracle connection class"""
        return OracleConnection

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new Oracle connection"""
        logger.debug(f"Creating Oracle connection for ID: {connection_id}")
        try:
            if connection_id not in self._config:
                logger.warning(f"No configuration found for connection ID: {connection_id}")
                return None

            config = self._config[connection_id]
            connection = OracleConnection(config)
            await connection.connect()
            logger.info(f"Oracle connection created successfully for ID: {connection_id}")
            return connection
        except Exception as e:
            logger.error(f"Error creating Oracle connection: {str(e)}", exc_info=True)
            return None
