Feature: Logout Functionality
  As a logged in user
  I want to logout from OrangeHRM
  So that I can end my session

  Background:
    Given I am logged in via API

  @smoke @logout
  Scenario: Successful logout
    When I click on logout
    Then I should be logged out and redirected to login page
