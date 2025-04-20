"""
Connection hooks for Behave tests.
"""
import asyncio

from src.common.logging_config import setup_logging
from src.common.registry_and_connection_facade import RegistryAndConnectionFacade

# Setup logging for connection hooks
logger = setup_logging("connection_hooks", "DEBUG")


async def setup_connections(context):
    """Initialize all connections and providers"""
    logger.info("Starting connection setup process")

    try:
        # Create and initialize the registry facade
        # logger.debug("Creating RegistryAndConnectionFacade instance")
        context.registry_facade = RegistryAndConnectionFacade()

        # logger.info("Initializing registry facade")
        await context.registry_facade.initialize()
        # logger.info("Registry facade initialized successfully")

        # Get all providers and create connections for each
        # logger.debug("Retrieving all providers from registry")
        providers = await context.registry_facade.get_all_providers()

        if not providers:
            logger.warning("No providers found in registry")
            return

        logger.info(f"Found {len(providers)} providers: {', '.join(providers.keys())}")

        for service_type, provider in providers.items():
            logger.info(f"Processing provider for service type: {service_type}")
            logger.debug(f"Provider details: {provider}")

            # Create connection for each service type
            logger.info(f"Creating connection for service type: {service_type}")
            connection = await context.registry_facade.create_connections(service_type)

            if connection:
                # Store active connection for cleanup
                if not hasattr(context, 'active_connections'):
                    context.active_connections = set()
                    logger.debug("Initialized active_connections set")

                context.active_connections.add((service_type, connection))
                logger.info(f"Successfully created and stored connection for {service_type}")
                logger.debug(f"Connection details: {connection}")
            else:
                logger.warning(f"Failed to create connection for {service_type}")

    except Exception as e:
        logger.error(f"Error during connection setup: {str(e)}", exc_info=True)
        raise


async def cleanup_connections(context):
    """Cleanup all connections"""
    logger.info("Starting connection cleanup process")
    try:
        if hasattr(context, 'registry_facade'):
            logger.debug("Shutting down registry facade")
            await context.registry_facade.shutdown()
            logger.info("Registry facade shutdown complete")
        else:
            logger.warning("No registry facade found to clean up")
    except Exception as e:
        logger.error(f"Error during connection cleanup: {str(e)}", exc_info=True)


def before_all(context):
    """Setup before all tests"""
    logger.info("Starting test execution")

    try:
        # Setup event loop for async operations
        logger.debug("Setting up event loop")
        context.loop = asyncio.get_event_loop()
        context.loop.run_until_complete(setup_connections(context))
    except Exception as e:
        logger.error(f"Error in before_all hook: {str(e)}", exc_info=True)
        raise


def after_all(context):
    """Cleanup after all tests"""
    logger.info("Test execution completed, starting cleanup")
    try:
        if hasattr(context, 'loop'):
            logger.debug("Running cleanup connections")
            context.loop.run_until_complete(cleanup_connections(context))
            logger.debug("Closing event loop")
            context.loop.close()
        else:
            logger.warning("No event loop found to clean up")
    except Exception as e:
        logger.error(f"Error in after_all hook: {str(e)}", exc_info=True)


def before_scenario(context, scenario):
    """Setup before each scenario"""
    logger.info(f"Starting scenario: {scenario.name}")
    # Reset any scenario-specific connection state
    context.active_connections = set()
    logger.debug("Reset active_connections set for new scenario")


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    logger.info(f"Completed scenario: {scenario.name}")
    try:
        if hasattr(context, 'active_connections'):
            logger.debug(f"Cleaning up {len(context.active_connections)} active connections")
            for service_type, connection in context.active_connections:
                logger.info(f"Closing connection for {service_type}")
                logger.debug(f"Connection details: {connection}")
                context.loop.run_until_complete(
                    context.registry_facade.close_connection(service_type, connection)
                )
                logger.debug(f"Successfully closed connection for {service_type}")
        else:
            logger.debug("No active connections to clean up")
    except Exception as e:
        logger.error(f"Error in after_scenario hook: {str(e)}", exc_info=True)
