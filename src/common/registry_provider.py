"""
Registry provider for managing service providers.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List, Optional
from src.base_classes.base_connection_provider import BaseConnectionProvider
from .service_registry import ServiceRegistry


class RegistryProvider:
    """Implementation of the registry provider interface that manages ServiceRegistry"""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the registry provider"""
        async with self._lock:
            if not self._initialized:
                ServiceRegistry.initialize()
                self._initialized = True

    async def register(self, service_type: str, provider: BaseConnectionProvider) -> None:
        """Register a provider with a service type"""
        async with self._lock:
            if not self._initialized:
                await self.initialize()
            # Update the ServiceRegistry
            ServiceRegistry._providers[service_type] = provider

    async def unregister(self, service_type: str) -> None:
        """Unregister a provider by service type"""
        async with self._lock:
            if service_type in ServiceRegistry._providers:
                del ServiceRegistry._providers[service_type]

    async def get(self, service_type: str) -> Optional[BaseConnectionProvider]:
        """Get a provider by service type"""
        async with self._lock:
            if not self._initialized:
                await self.initialize()
            return ServiceRegistry.get_provider(service_type)

    async def get_all(self) -> Dict[str, BaseConnectionProvider]:
        """Get all registered providers"""
        async with self._lock:
            if not self._initialized:
                await self.initialize()
            return ServiceRegistry.get_all_providers()

    async def clear(self) -> None:
        """Clear all registered providers"""
        async with self._lock:
            ServiceRegistry.reset()
            self._initialized = False
