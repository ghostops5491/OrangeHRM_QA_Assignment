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
