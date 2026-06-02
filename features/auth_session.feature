Feature: Authentication Session Persistence
  As a logged in user
  I want my session to persist
  So that I can navigate directly to authenticated pages without re-logging in

  Background:
    Given I am logged in via API

  @smoke @auth-session @SIT
  Scenario: Verify session persists after navigating away and back
    When I navigate to the dashboard
    Then I should see the dashboard page
    When I logout
    And I navigate to the dashboard again
    Then I should be redirected to the login page

  @regression @dashboard @auth-session
  Scenario: Dashboard quick launch widgets are visible for authenticated user
    When I navigate to the dashboard
    Then I should see the dashboard quick launch section
