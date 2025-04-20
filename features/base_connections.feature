#Feature: Base Connections
#  As a test engineer
#  I want to have common connection setup
#  So that I can reuse it across different feature files
#
#  Background:
#    Given I have a Remote Command Service connection to "remote_command_prod"
#    And I have a Remote Search Service connection to "remote_search_prod"
#    And I have a QuickFix connection to "quickfix_prod"
#    And I have an IMIX connection to "imix_prod"
#
#  # This is a template scenario that will be used to generate actual scenarios
#  Scenario Template: Connection Health Check
#    Given I have a "<service_type>" connection to "<service_name>"
#    When I check the connection health
#    Then the connection should be healthy
#    And the connection status should be "connected"
#
#    Examples:
#      | service_type        | service_name        |
#      | remote_command      | remote_command_prod |
#      | remote_search       | remote_search_prod  |
#      | quickfix           | quickfix_prod       |
#      | imix               | imix_prod           |