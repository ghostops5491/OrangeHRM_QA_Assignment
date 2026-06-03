Feature: User Management
  As an admin
  I want to manage users in OrangeHRM
  So that I can maintain user accounts

  Background:
    Given I am logged in via API
    And I am on the Admin page

  @smoke @user-management @user-search
  Scenario: Search for an existing user
    When I search for user "Admin"
    Then I should see the user in search results

  @regression @user-management @user-search @validation
  Scenario: Search for a non-existing user
    When I search for user "non_existing_user_123"
    Then I should see no user records in search results

  @regression @user-management @filter @SIT
  Scenario: Reset search filter
    When I search for user "Admin"
    And I reset the search filter
    Then all users should be displayed

  @regression @user-management @user-create
  Scenario: Open add user form
    When I click add user
    Then I should see the add user form

  @regression @user-management @user-create @SIT
  Scenario: Create and Verify a new System User
    Given a new employee is created in PIM
    When I navigate to the Admin page
    And I click add user
    And I fill the user form with role "ESS" and status "Enabled"
    And I click save user
    Then the user should be created successfully
    And I search for the newly created user
    Then I should see the user in search results with role "ESS" and status "Enabled"

  @regression @user-management @user-update @SIT
  Scenario: Update status of an existing user
    Given a new employee is created in PIM
    And a new System User is created for that employee
    When I navigate to the Admin page
    And I search for the newly created user
    And I click edit for the newly created user
    And I change user status to "Disabled"
    And I click save user
    Then the user should be updated successfully
    And I search for the newly created user
    Then I should see the user in search results with role "ESS" and status "Disabled"

  @regression @user-management @validation
  Scenario Outline: Validate User form field errors
    When I click add user
    And I fill user form with role "<role>", status "<status>", employee "<employee>", username "<username>", password "<password>"
    And I click save user
    Then I should see field validation message "<error_message>" for "<field>"

    Examples:
      | role   | status   | employee | username | password  | field     | error_message                  |
      | ESS    | Enabled  | Admin    | abc      | Admin123! | Username  | Should be at least 5 characters|
      | Select | Enabled  | Admin    | UniqueU  | Admin123! | User Role | Required                       |
