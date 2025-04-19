# """
# Behave hooks for test setup and teardown.
# """

# import asyncio
# from behave.model import Scenario, Feature
# from src.services import ServiceFacade, initialize_services
# from src.common import ConfigLoader

# async def setup_connections(context):
#     """Initialize all connections and providers"""
#     # Initialize the service facade
#     context.service_facade = await initialize_services()

# async def cleanup_connections(context):
#     """Cleanup all connections"""
#     if hasattr(context, 'service_facade'):
#         await context.service_facade.shutdown()

# def before_all(context):
#     """Setup before all tests"""
#     # Load global configuration
#     context.config = ConfigLoader.load_config("config.yaml")
    
#     # Setup event loop for async operations
#     context.loop = asyncio.get_event_loop()
#     context.loop.run_until_complete(setup_connections(context))

# def after_all(context):
#     """Cleanup after all tests"""
#     context.loop.run_until_complete(cleanup_connections(context))
#     context.loop.close()

# def before_feature(context, feature):
#     """Setup before each feature"""
#     pass

# def after_feature(context, feature):
#     """Cleanup after each feature"""
#     pass

# def before_scenario(context, scenario):
#     """Setup before each scenario"""
#     # Reset any scenario-specific connection state
#     context.active_connections = set()

# def after_scenario(context, scenario):
#     """Cleanup after each scenario"""
#     # Close any scenario-specific connections
#     if hasattr(context, 'active_connections'):
#         for service_type, connection_id in context.active_connections:
#             context.loop.run_until_complete(
#                 context.service_facade.close_connection(service_type, connection_id)
#             ) 