"""
Connection hooks for Behave tests.
"""

import asyncio

from src.common.registry_and_connection_facade import RegistryAndConnectionFacade


async def setup_connections(context):
    """Initialize all connections and providers"""
    # Create and initialize the registry facade
    context.registry_facade = RegistryAndConnectionFacade()
    await context.registry_facade.initialize()

    # Get all providers and create connections for each
    providers = await context.registry_facade.get_all_providers()
    for service_type, provider in providers.items():
        # Create connection for each service type
        connection = await context.registry_facade.create_connection(service_type)
        if connection:
            # Store active connection for cleanup
            if not hasattr(context, 'active_connections'):
                context.active_connections = set()
            context.active_connections.add((service_type, connection))


async def cleanup_connections(context):
    """Cleanup all connections"""
    if hasattr(context, 'registry_facade'):
        await context.registry_facade.shutdown()


def before_all(context):
    pass
    """Setup before all tests"""
    # Load global configuration
    # context.config = ConfigLoader.load_config("config.yaml")

    # Setup event loop for async operations
    # context.loop = asyncio.get_event_loop()
    # context.loop.run_until_complete(setup_connections(context))


def after_all(context):
    """Cleanup after all tests"""
    # context.loop.run_until_complete(cleanup_connections(context))
    # context.loop.close()
    pass


def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Reset any scenario-specific connection state
    context.active_connections = set()


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    if hasattr(context, 'active_connections'):
        for service_type, connection_id in context.active_connections:
            context.loop.run_until_complete(
                context.registry_facade.close_connection(service_type, connection_id)
            )
