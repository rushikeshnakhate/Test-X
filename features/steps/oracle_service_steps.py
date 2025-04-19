# from behave import given, when, then
# from src.services.oracle.oracle_service import OracleService
# import asyncio
#
#
# @given('the configuration is loaded from "{config_file}"')
# def step_impl(context, config_file):
#     context.config = ConfigLoader.load_config(config_file)
#
#
# @given('I have initialized the Oracle service "{service_name}"')
# def step_impl(context, service_name):
#     services = ConfigLoader.get_enabled_services('database')
#     if service_name not in services:
#         raise ValueError(f"Service {service_name} not found in configuration")
#
#     context.oracle_service = OracleService(services[service_name])
#     asyncio.run(context.oracle_service.initialize())
#
#
# @when('I check the database health')
# def step_impl(context):
#     context.health_result = asyncio.run(context.oracle_service.health_check())
#
#
# @then('the health check should return "{expected}"')
# def step_impl(context, expected):
#     assert str(context.health_result).lower() == expected.lower()
#
#
# @when('I execute the query "{query}"')
# def step_impl(context, query):
#     context.query_result = asyncio.run(context.oracle_service.execute_query(query))
#
#
# @when('I execute the query "{query}" with parameters {parameters}')
# def step_impl(context, query, parameters):
#     import ast
#     params = ast.literal_eval(parameters)
#     context.query_result = asyncio.run(context.oracle_service.execute_query(query, params))
#
#
# @then('the query should execute successfully')
# def step_impl(context):
#     assert context.query_result is not None
#
#
# @then('the result should contain "{expected}"')
# def step_impl(context, expected):
#     assert any(str(expected) in str(row) for row in context.query_result)
