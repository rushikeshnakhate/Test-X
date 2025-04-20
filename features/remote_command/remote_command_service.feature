#Feature: Remote Command Service
#  As a user
#  I want to execute commands through a Remote Command Service
#  So I can interact with remote systems
#
#  Background:
#    Given the following command services are configured:
#      | name     | endpoint               |
#      | service1 | http://service1.local  |
#      | service2 | http://service2.local  |
#
#  Scenario: Execute simple command
#    Given I have a Remote Command Service connection to "service1"
#    When I execute the command "status"
#    Then the command should execute successfully
#
#  Scenario: Execute command with table parameters
#    Given I have a Remote Command Service connection to "service2"
#    When I execute the command "configure" with parameters
#      | parameter | value |
#      | timeout   | 30    |
#      | retries   | 3     |
#    Then the command result should contain "success"
#
#  Scenario: Execute command with JSON parameters
#    Given I have a Remote Command Service connection to "service1"
#    When I execute the command "update" with parameters
#    """
#    {
#      "version": "2.1.0",
#      "force": false
#    }
#    """
#    Then the command result should match
#    """
#    {"status": "updated"}
#    """
#
#  Scenario: List available commands
#    Given I have a Remote Command Service connection to "service1"
#    When I list available commands
#    Then the available commands should include "diagnostics"