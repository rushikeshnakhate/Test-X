"""QuickFix provider implementation"""

from typing import Dict, Any, Type, Optional

from src.base_classes.base_connection import BaseConnection
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.common.logging_config import setup_logging
from src.services.quickfix.quickfix_service import QuickFixConnection

# Setup logging for QuickFix provider
logger = setup_logging("quickfix_provider", "DEBUG")


class QuickFixProvider(BaseConnectionProvider):
    """Provider for QuickFix connections"""

    def __init__(self):
        """Initialize the QuickFix provider."""
        logger.info("Initializing QuickFixProvider")
        super().__init__()
        logger.debug("QuickFix provider initialized")

    async def load_config(self) -> None:
        """Load QuickFix-specific configuration"""
        logger.debug("Loading QuickFix configuration")
        try:
            # Get configuration from config loader
            all_configs = self._config_loader.get_all_configs()
            if not all_configs or 'config' not in all_configs:
                logger.warning("No configuration found in config loader")
                return

            # Extract QuickFix configuration from the nested config structure
            cfg = all_configs['config'].get('quickfix')
            if not cfg:
                logger.warning(
                    f"No QuickFix configuration found in config, available services: {list(all_configs['config'].keys())}")
                return

            # Extract QuickFix configuration
            if cfg.get('enable', True):
                connections = cfg.get('connections', [])
                for conn in connections:
                    if conn.get('enable', True):
                        connection_id = conn.get('name', 'default')
                        self._enabled_connections.append(connection_id)
                        self._config[connection_id] = conn
                logger.info("QuickFix configuration loaded successfully")
                logger.debug(f"Enabled connections: {self._enabled_connections}")
            else:
                logger.info("QuickFix provider is disabled in configuration")
        except Exception as e:
            logger.error(f"Error loading QuickFix configuration: {str(e)}", exc_info=True)
            raise

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the QuickFix connection class"""
        return QuickFixConnection

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new QuickFix connection"""
        logger.debug(f"Creating QuickFix connection for ID: {connection_id}")
        try:
            if connection_id not in self._config:
                logger.warning(f"No configuration found for connection ID: {connection_id}")
                return None

            config = self._config[connection_id]
            connection = QuickFixConnection(config)
            await connection.connect()
            logger.info(f"QuickFix connection created successfully for ID: {connection_id}")
            return connection
        except Exception as e:
            logger.error(f"Error creating QuickFix connection: {str(e)}", exc_info=True)
            return None
