Feature: Login Functionality
  As a user
  I want to login to OrangeHRM
  So that I can access the application

  Background:
    Given I am on the OrangeHRM login page

  @smoke @login
  Scenario: Successful login with valid credentials
    When I enter valid username and password
    And I click on login button
    Then I should be logged in successfully

  @regression @login @validation
  Scenario: Unsuccessful login with invalid credentials
    When I enter invalid username and password
    And I click on login button
    Then I should see an error message

  @regression @login @validation @required-fields
  Scenario Outline: Login with missing required fields
    When I enter username state "<username>" and password state "<password>"
    And I click on login button
    Then I should see required field messages

    Examples:
      | username | password  |
      | blank    | blank     |
      | blank    | admin123  |
      | Admin    | blank     |

  @regression @login @password-reset
  Scenario: Navigate to forgot password page
    When I click the forgot password link
    Then I should see the reset password page
