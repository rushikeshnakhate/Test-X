from behave import given, when, then
import json
from src.services.remote_command_service.client import RemoteCommandConnection

@given('I have a Remote Command Service connection to "{service_name}"')
def step_impl(context, service_name):
    services = context.config.command_services
    service_config = next((s for s in services if s.name == service_name), None)
    if not service_config:
        raise ValueError(f"Service {service_name} not found in configuration")
    
    # Get connection from pool
    connection_id = f"remote_command_{service_name}"
    context.active_connections.add(("remote_command", connection_id))
    context.current_connection = context.loop.run_until_complete(
        context.connection_pool.get_connection("remote_command", connection_id, service_config)
    )

@when('I execute the command "{command}"')
def step_impl(context, command):
    if not hasattr(context, 'current_connection'):
        raise RuntimeError("No active Remote Command Service connection")
    
    params = {}
    if context.table:
        for row in context.table:
            params[row['parameter']] = row['value']
    
    context.command_result = context.loop.run_until_complete(
        context.current_connection.execute_command(command, params)
    )

@when('I execute the command "{command}" with parameters')
def step_impl(context, command):
    if not hasattr(context, 'current_connection'):
        raise RuntimeError("No active Remote Command Service connection")
    
    params = json.loads(context.text) if context.text else {}
    context.command_result = context.loop.run_until_complete(
        context.current_connection.execute_command(command, params)
    )

@then('the command should execute successfully')
def step_impl(context):
    assert context.command_result is not None

@then('the command result should contain "{expected_value}"')
def step_impl(context, expected_value):
    assert expected_value in str(context.command_result)

@then('the command result should match')
def step_impl(context):
    expected = json.loads(context.text)
    assert context.command_result == expected

@when('I list available commands')
def step_impl(context):
    if not hasattr(context, 'current_connection'):
        raise RuntimeError("No active Remote Command Service connection")
    
    context.available_commands = context.loop.run_until_complete(
        context.current_connection.list_available_commands()
    )

@then('the available commands should include "{command}"')
def step_impl(context, command):
    assert command in context.available_commands 