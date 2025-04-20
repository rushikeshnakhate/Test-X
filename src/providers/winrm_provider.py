"""
WinRM connection provider implementation.
"""
from typing import Dict, Any, Optional, Type
from src.common.logging_config import setup_logging, get_logger
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.base_classes.base_connection import BaseConnection
from src.connections.winrm_connection import WinRMConnection

# Setup logging for WinRM provider
logger = setup_logging("winrm_provider", "DEBUG")


class WinRMProvider(BaseConnectionProvider):
    """Provider for WinRM connections."""

    def __init__(self):
        """Initialize the WinRM provider."""
        logger.info("Initializing WinRMProvider")
        super().__init__()
        self._connection_class = WinRMConnection
        logger.debug("WinRM provider initialized with WinRMConnection class")

    async def load_config(self) -> None:
        """Load WinRM-specific configuration."""
        logger.debug("Loading WinRM configuration")
        try:
            # Get configuration from config loader
            cfg = self._config_loader.get_config('winrm')
            if not cfg:
                logger.warning("No WinRM configuration found")
                return

            # Extract WinRM configuration
            if cfg.get('enable', True):
                connections = cfg.get('connections', [])
                for conn in connections:
                    if conn.get('enable', True):
                        connection_id = conn.get('name', 'default')
                        self._enabled_connections.append(connection_id)
                        self._config[connection_id] = conn
                logger.info("WinRM configuration loaded successfully")
                logger.debug(f"Enabled connections: {self._enabled_connections}")
            else:
                logger.info("WinRM provider is disabled in configuration")
        except Exception as e:
            logger.error(f"Error loading WinRM configuration: {str(e)}", exc_info=True)
            raise

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the WinRM connection class"""
        return self._connection_class

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new WinRM connection"""
        logger.debug(f"Creating WinRM connection for ID: {connection_id}")
        try:
            if connection_id not in self._config:
                logger.warning(f"No configuration found for connection ID: {connection_id}")
                return None

            config = self._config[connection_id]
            connection = self._connection_class(config)
            await connection.connect()
            logger.info(f"WinRM connection created successfully for ID: {connection_id}")
            return connection
        except Exception as e:
            logger.error(f"Error creating WinRM connection: {str(e)}", exc_info=True)
            return None

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate WinRM configuration."""
        logger.debug("Validating WinRM configuration")
        try:
            required_fields = ["host", "port", "username", "password", "transport"]
            for field in required_fields:
                if field not in config:
                    logger.error(f"Missing required field: {field}")
                    return False
            logger.info("WinRM configuration validation successful")
            return True
        except Exception as e:
            logger.error(f"WinRM configuration validation failed: {str(e)}", exc_info=True)
            return False

    async def get_health_status(self) -> Dict[str, Any]:
        """Get WinRM provider health status."""
        logger.debug("Getting WinRM provider health status")
        try:
            # Implement WinRM-specific health check
            status = {
                "status": "healthy",
                "provider": "winrm",
                "connections": len(self._connections)
            }
            logger.debug(f"Health status: {status}")
            return status
        except Exception as e:
            logger.error(f"Error getting WinRM health status: {str(e)}", exc_info=True)
            return {"status": "unhealthy", "error": str(e)}

    async def shutdown(self) -> None:
        """Shutdown the WinRM provider."""
        logger.info("Shutting down WinRM provider")
        try:
            # Close all active connections
            for connection in self._connections.values():
                try:
                    await connection.close()
                    logger.debug(f"Closed connection: {connection.id}")
                except Exception as e:
                    logger.error(f"Error closing connection {connection.id}: {str(e)}", exc_info=True)
            
            self._connections.clear()
            logger.info("WinRM provider shutdown completed")
        except Exception as e:
            logger.error(f"Error during WinRM provider shutdown: {str(e)}", exc_info=True)
            raise 