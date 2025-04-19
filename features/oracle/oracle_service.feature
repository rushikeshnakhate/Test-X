Feature: Oracle Database Service Tests
  As a test engineer
  I want to verify Oracle database connectivity and operations
  So that I can ensure the database service is working correctly

  Background:
    Given the configuration is loaded from "config.yaml"
    And I have initialized the Oracle service "oracle_prod"

  Scenario: Verify database connection
    When I check the database health
    Then the health check should return "True"

  Scenario: Execute simple query
    When I execute the query "SELECT 1 FROM DUAL"
    Then the query should execute successfully
    And the result should contain "1"

  Scenario: Execute parameterized query
    When I execute the query "SELECT :1 FROM DUAL" with parameters {"1": 42}
    Then the query should execute successfully
    And the result should contain "42" 