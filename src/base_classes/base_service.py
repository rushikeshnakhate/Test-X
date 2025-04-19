from abc import ABC, abstractmethod
from typing import Any, Optional
from .base_connection import BaseConnection

class BaseService(ABC):
    def __init__(self, config: Any):
        self.config = config
        self._connection: Optional[BaseConnection] = None

    @property
    def connection(self) -> Optional[BaseConnection]:
        return self._connection

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service and establish connection"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service and close connections"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the service is healthy"""
        pass

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown() 