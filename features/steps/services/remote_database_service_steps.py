import json
from behave import given, when, then

from typing import List, Tuple


class DatabaseContext:
    """Manages state for database operations"""

    def __init__(self, context):
        self.context = context
        self.connection = None
        self.query_result = None
        self.error = None
        self.columns: List[str] = []
        self.rows: List[Tuple] = []
        self.affected_rows = 0

    async def execute_query(self, query: str, params: List[Any] = None):
        """Execute query and handle results"""
        try:
            if query.strip().upper().startswith("SELECT"):
                self.columns, self.rows = await self.connection.select(query, params)
                self.affected_rows = len(self.rows)
            elif query.strip().upper().startswith("INSERT"):
                self.affected_rows = await self.connection.insert(query, params)
            elif query.strip().upper().startswith("UPDATE"):
                self.affected_rows = await self.connection.update(query, params)
            elif query.strip().upper().startswith("DELETE"):
                self.affected_rows = await self.connection.delete(query, params)
            else:
                self.query_result = await self.connection.execute(query, params)
        except Exception as e:
            self.error = str(e)


@given('the following database services are configured')
def step_configure_services(context):
    """Setup mock database services"""
    if not hasattr(context.config, 'database_services'):
        context.config.database_services = []
    for row in context.table:
        context.config.database_services.append({
            'name': row['name'],
            'host': row['host'],
            'port': int(row['port'])
        })


@given('I have a Remote Database Service connection to "{service_name}"')
def step_connect_to_database(context, service_name):
    """Establish connection to database service"""
    if not hasattr(context, 'db'):
        context.db = DatabaseContext(context)

    service_config = next(
        (s for s in context.config.database_services if s['name'] == service_name),
        None
    )
    if not service_config:
        raise ValueError(f"Database service '{service_name}' not configured")

    context.db.connection = context.loop.run_until_complete(
        context.connection_pool.get_connection(
            "remote_database",
            f"db_conn_{service_name}",
            service_config
        )
    )
    context.loop.run_until_complete(context.db.connection.connect())


@when('I execute the SELECT query "{query}" with parameters:')
def step_execute_select(context, query):
    """Execute SELECT query with parameters"""
    params = [row[0] for row in context.table.rows] if context.table else []
    context.loop.run_until_complete(
        context.db.execute_query(query, params)
    )


@when('I execute the INSERT query "{query}" with parameters:')
def step_execute_insert(context, query):
    """Execute INSERT query with parameters"""
    params = [row[0] for row in context.table.rows] if context.table else []
    context.loop.run_until_complete(
        context.db.execute_query(query, params)
    )


@when('I execute the UPDATE query "{query}" with parameters:')
def step_execute_update(context, query):
    """Execute UPDATE query with parameters"""
    params = [row[0] for row in context.table.rows] if context.table else []
    context.loop.run_until_complete(
        context.db.execute_query(query, params)
    )


@when('I execute the DELETE query "{query}" with parameters:')
def step_execute_delete(context, query):
    """Execute DELETE query with parameters"""
    params = [row[0] for row in context.table.rows] if context.table else []
    context.loop.run_until_complete(
        context.db.execute_query(query, params)
    )


@when('I execute the invalid query "{query}"')
def step_execute_invalid_query(context, query):
    """Execute query expected to fail"""
    context.loop.run_until_complete(
        context.db.execute_query(query)
    )


@then('the connection should be active')
def step_verify_connection_active(context):
    """Verify database connection is active"""
    assert context.db.connection._is_connected, "Database connection is not active"


@then('the query should return {row_count:int} row(s)')
def step_verify_row_count(context, row_count):
    """Verify query returned expected number of rows"""
    assert len(context.db.rows) == row_count, (
        f"Expected {row_count} rows, got {len(context.db.rows)}"
    )


@then('the result should contain column "{column_name}"')
def step_verify_column_exists(context, column_name):
    """Verify result contains specific column"""
    assert column_name in context.db.columns, (
        f"Column '{column_name}' not found in results"
    )


@then('the operation should affect {row_count:int} row(s)')
def step_verify_affected_rows(context, row_count):
    """Verify DML operation affected expected rows"""
    assert context.db.affected_rows == row_count, (
        f"Expected to affect {row_count} rows, got {context.db.affected_rows}"
    )


@then('the operation should fail with error')
def step_verify_operation_failed(context):
    """Verify operation failed as expected"""
    assert context.db.error is not None, "Operation should have failed but succeeded"
