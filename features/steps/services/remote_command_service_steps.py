import json
from behave import given, when, then


class RemoteCommandContext:
    """Helper class to manage remote command state"""

    def __init__(self, context):
        self.context = context
        self.connection = None
        self.result = None
        self.available_commands = []

    def get_service_config(self, service_name):
        """Find service configuration by name"""
        services = self.context.config.command_services
        service = next((s for s in services if s.name == service_name), None)
        if not service:
            raise ValueError(f"Service '{service_name}' not found in configuration")
        return service

    async def execute(self, command, params=None):
        """Execute command with parameters"""
        if not self.connection:
            raise RuntimeError("No active connection")
        return await self.connection.execute_command(command, params or {})

    async def list_commands(self):
        """List available commands"""
        if not self.connection:
            raise RuntimeError("No active connection")
        return await self.connection.list_available_commands()


@given('I have a Remote Command Service connection to "{service_name}"')
def step_connect_to_service(context, service_name):
    """Establish connection to specified service"""
    if not hasattr(context, 'cmd'):
        context.cmd = RemoteCommandContext(context)

    service_config = context.cmd.get_service_config(service_name)
    connection_id = f"remote_command_{service_name}"

    context.active_connections.add(("remote_command", connection_id))
    context.cmd.connection = context.loop.run_until_complete(
        context.connection_pool.get_connection(
            "remote_command",
            connection_id,
            service_config
        )
    )


@when('I execute the command "{command}"')
def step_execute_command(context, command):
    """Execute command with optional table parameters"""
    params = {}
    if hasattr(context, 'table'):
        params = {row['parameter']: row['value'] for row in context.table}

    context.cmd.result = context.loop.run_until_complete(
        context.cmd.execute(command, params)
    )


@when('I execute the command "{command}" with parameters')
def step_execute_command_with_json(context, command):
    """Execute command with JSON parameters"""
    params = json.loads(context.text) if context.text else {}
    context.cmd.result = context.loop.run_until_complete(
        context.cmd.execute(command, params)
    )


@when('I list available commands')
def step_list_commands(context):
    """List all available commands"""
    context.cmd.available_commands = context.loop.run_until_complete(
        context.cmd.list_commands()
    )


@then('the command should execute successfully')
def step_verify_success(context):
    """Verify command executed without errors"""
    assert context.cmd.result is not None, "Command returned no result"


@then('the command result should contain "{expected_value}"')
def step_verify_result_contains(context, expected_value):
    """Verify result contains expected string"""
    assert expected_value in str(context.cmd.result), (
        f"Result '{context.cmd.result}' does not contain '{expected_value}'"
    )


@then('the command result should match')
def step_verify_result_matches(context):
    """Verify result matches expected JSON"""
    expected = json.loads(context.text)
    assert context.cmd.result == expected, (
        f"Expected {expected}, got {context.cmd.result}"
    )


@then('the available commands should include "{command}"')
def step_verify_command_available(context, command):
    """Verify command is in available commands list"""
    assert command in context.cmd.available_commands, (
        f"Command '{command}' not found in available commands"
    )
