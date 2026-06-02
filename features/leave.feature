Feature: Leave Management and Navigation
  As an HR admin
  I want to manage Leave records and navigate across different HR modules
  So that I can quickly view leave requests and transition between PIM and Leave sections

  Background:
    Given I am logged in via API

  @regression @leave @leave-list
  Scenario: Open Leave list
    When I navigate to the Leave list
    Then I should see the leave list page

  @regression @leave @navigation @SIT
  Scenario: Navigate between PIM and Leave pages
    When I navigate to the PIM employee list
    Then I should see the employee list page
    When I navigate to the Leave list
    Then I should see the leave list page
