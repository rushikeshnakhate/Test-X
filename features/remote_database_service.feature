Feature: Remote Database Service
  As an application
  I want to interact with a remote database
  So I can perform CRUD operations securely

#  Background:
#    Given the following database services are configured:
#      | name       | host           | port |
#      | primary_db | db.example.com | 5432 |
#      | backup_db  | backup.db.com  | 5432 |

  Scenario: Successful database connection
    Given I have a Remote Database Service connection to "primary_db"
    Then the connection should be active

#  Scenario: Execute SELECT query
#    Given I have a Remote Database Service connection to "primary_db"
#    When I execute the SELECT query "SELECT * FROM users WHERE id = $1" with parameters:
#      | 1 |
#    Then the query should return 1 row
#    And the result should contain column "username"
#
#  Scenario: Execute INSERT query
#    Given I have a Remote Database Service connection to "primary_db"
#    When I execute the INSERT query "INSERT INTO users (username, email) VALUES ($1, $2)" with parameters:
#      | testuser | test@example.com |
#    Then the operation should affect 1 row
#
#  Scenario: Execute UPDATE query
#    Given I have a Remote Database Service connection to "primary_db"
#    When I execute the UPDATE query "UPDATE users SET email = $1 WHERE id = $2" with parameters:
#      | updated@example.com | 1 |
#    Then the operation should affect 1 row
#
#  Scenario: Execute DELETE query
#    Given I have a Remote Database Service connection to "primary_db"
#    When I execute the DELETE query "DELETE FROM users WHERE id = $1" with parameters:
#      | 1 |
#    Then the operation should affect 1 row
#
#  Scenario: Handle query error
#    Given I have a Remote Database Service connection to "primary_db"
#    When I execute the invalid query "SELECT * FROM non_existent_table"
#    Then the operation should fail with error