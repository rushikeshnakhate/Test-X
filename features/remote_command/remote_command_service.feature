Feature: Remote Command Service Tests
  As a test engineer
  I want to verify Remote Command Service functionality
  So that I can ensure remote commands are executed correctly

  Background:
    Given I have a Remote Command Service connection to "remote_command_prod"

  Scenario: List available commands
    When I list available commands
    Then the available commands should include "status"
    And the available commands should include "restart"

  Scenario: Execute simple command
    When I execute the command "status"
    Then the command should execute successfully
    And the command result should contain "running"

  Scenario: Execute command with table parameters
    When I execute the command "configure"
      | parameter | value     |
      | mode     | debug     |
      | level    | verbose   |
    Then the command should execute successfully
    And the command result should contain "configured"

  Scenario: Execute command with JSON parameters
    When I execute the command "update" with parameters
      """
      {
        "component": "service",
        "version": "1.2.3",
        "force": true
      }
      """
    Then the command should execute successfully
    And the command result should match
      """
      {
        "status": "success",
        "updated": true,
        "version": "1.2.3"
      }
      """ 