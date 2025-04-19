from abc import ABC, abstractmethod
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential


class BaseConnection(ABC):
    def __init__(self, config: Any):
        self.config = config
        self._connected = False
        self._connection = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the service"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the connection is healthy"""
        pass

    async def __aenter__(self):
        await this.connect()
        return this

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await this.disconnect()
