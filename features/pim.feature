Feature: PIM Employee Management
  As an HR admin
  I want to manage employees in PIM
  So that I can view, search, and add employee records

  Background:
    Given I am logged in via API

  @regression @pim @employee-list
  Scenario: Open PIM employee list
    When I navigate to the PIM employee list
    Then I should see the employee list page

  @regression @pim @employee-search
  Scenario: Search employee list by employee name
    When I navigate to the PIM employee list
    And I search employees by name "Admin"
    Then employee search results should be shown

  @regression @pim @employee-create @SIT
  Scenario: Add a new employee
    When I navigate to the PIM employee list
    And I open the add employee form
    And I add an employee with generated details
    Then the employee should be created successfully
