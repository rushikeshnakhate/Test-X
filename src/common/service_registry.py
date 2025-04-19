"""
Service registry for managing service providers.
"""

from typing import Dict, Optional

from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.services.imix_service.imix_provider import IMIXProvider
from src.services.quickfix.quickfix_provider import QuickFixProvider
from src.services.remote_command_service.command_provider import RemoteCommandProvider
from src.services.remote_search_service.remote_search_provider import RemoteSearchProvider


class ServiceRegistry:
    """
    Registry for service providers.
    Uses the singleton pattern to ensure only one instance of each provider type exists.
    """

    _providers: Dict[str, BaseConnectionProvider] = {}
    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """Initialize the registry by creating provider instances"""
        if cls._initialized:
            return

        # Create provider instances - one per provider type
        cls._providers["remote_command"] = RemoteCommandProvider()
        cls._providers["remote_search"] = RemoteSearchProvider()
        cls._providers["quickfix"] = QuickFixProvider()
        cls._providers["imix"] = IMIXProvider()
        cls._initialized = True

    @classmethod
    def get_provider(cls, service_type: str) -> Optional[BaseConnectionProvider]:
        """Get a provider instance by service type"""
        if not cls._initialized:
            cls.initialize()

        return cls._providers.get(service_type)

    @classmethod
    def get_all_providers(cls) -> Dict[str, BaseConnectionProvider]:
        """Get all registered provider instances"""
        if not cls._initialized:
            cls.initialize()

        return cls._providers

    @classmethod
    def reset(cls) -> None:
        """Reset the registry"""
        cls._providers = {}
        cls._initialized = False


def get_all_services_providers() -> Dict[str, BaseConnectionProvider]:
    """Get all registered service providers"""
    return ServiceRegistry.get_all_providers()
