import uuid
from behave import given, when, then, step
from features.pages.login_page import LoginPage
from features.pages.dashboard_page import DashboardPage
from features.pages.admin_page import AdminPage
from config.config import Config
from utils.logger import get_logger
from utils.api_helper import APIHelper

logger = get_logger(__name__)


@given("I am logged in as admin")
def step_impl(context):
    # Use UI login (for login-related tests)
    login_page = LoginPage(context.page)
    login_page.navigate()
    login_page.login(Config.ADMIN_USERNAME, Config.ADMIN_PASSWORD)
    dashboard_page = DashboardPage(context.page)
    assert dashboard_page.is_dashboard_displayed()
    context.dashboard_page = dashboard_page


@given("I am logged in via API")
def step_impl(context):
    # Fallback to UI login as API login cookies do not reliably bypass live website CSRF/bot protections
    login_page = LoginPage(context.page)
    login_page.navigate()
    login_page.login(Config.ADMIN_USERNAME, Config.ADMIN_PASSWORD)
    dashboard_page = DashboardPage(context.page)
    assert dashboard_page.is_dashboard_displayed()
    context.dashboard_page = dashboard_page



@given("I am on the Admin page")
@step("I navigate to the Admin page")
def step_impl(context):
    context.dashboard_page.go_to_admin_page()
    admin_page = AdminPage(context.page)
    assert admin_page.is_admin_page_displayed()
    context.admin_page = admin_page


@when('I search for user "{username}"')
def step_impl(context, username):
    context.admin_page.search_user(username)


@then("I should see the user in search results")
def step_impl(context):
    assert context.admin_page.is_search_results_displayed(), "User not found in search results"


@then("I should see no user records in search results")
def step_impl(context):
    assert context.admin_page.is_no_records_displayed(), "Expected no records message was not displayed"


@when("I reset the search filter")
def step_impl(context):
    context.admin_page.reset_search()


@then("all users should be displayed")
def step_impl(context):
    assert context.admin_page.is_username_filter_cleared(), "Search filter was not cleared"
    assert context.admin_page.is_search_results_displayed(), "Results table is not displayed after reset"


@when("I navigate to the dashboard")
def step_impl(context):
    context.page.goto(f"{Config.BASE_URL}/web/index.php/dashboard/index")


@then("I should see the dashboard page")
def step_impl(context):
    dashboard_page = DashboardPage(context.page)
    assert dashboard_page.is_dashboard_displayed()
    context.dashboard_page = dashboard_page


@then("I should see the dashboard quick launch section")
def step_impl(context):
    dashboard_page = DashboardPage(context.page)
    assert dashboard_page.is_quick_launch_displayed(), "Quick Launch section is not fully displayed"
    context.dashboard_page = dashboard_page


@when("I logout")
def step_impl(context):
    context.dashboard_page.logout()


@when("I click add user")
def step_impl(context):
    context.admin_page.click_add_user()


@when("I navigate to the dashboard again")
def step_impl(context):
    context.page.goto(f"{Config.BASE_URL}/web/index.php/dashboard/index")


@then("I should be redirected to the login page")
def step_impl(context):
    login_page = LoginPage(context.page)
    # Wait for login button to be visible to confirm we're on login page
    assert login_page.is_login_page_displayed(), "Not redirected to login page"


@then("I should see the add user form")
def step_impl(context):
    assert context.admin_page.is_add_user_form_displayed(), "Add User form was not displayed"


@step("a new employee is created in PIM")
def step_impl(context):
    context.execute_steps(u"""
        When I navigate to the PIM employee list
        And I open the add employee form
        And I add an employee with generated details
        Then the employee should be created successfully
    """)


@step('I fill the user form with role "{role}" and status "{status}"')
def step_impl(context, role, status):
    unique_id = uuid.uuid4().hex[:6]
    context.generated_username = f"user_{unique_id}"
    employee_name = f"{context.generated_first_name} {context.generated_last_name}"
    
    context.admin_page.fill_user_form(
        role=role,
        status=status,
        username=context.generated_username,
        password="Password123!",
        employee_name=employee_name
    )


@step("I click save user")
def step_impl(context):
    context.admin_page.save_user()


@step("the user should be created successfully")
def step_impl(context):
    logger.info("Waiting for success toast (up to 45 seconds)...")
    success = context.admin_page.is_visible(context.admin_page.success_toast, timeout=45000)
    assert success, "Success toast was not displayed after saving user (45s timeout)"
    context.page.wait_for_timeout(3000)


@step("I search for the newly created user")
def step_impl(context):
    context.admin_page.search_user(context.generated_username)


@step('I should see the user in search results with role "{role}" and status "{status}"')
def step_impl(context, role, status):
    actual_role, actual_status = context.admin_page.get_user_row_details(context.generated_username)
    assert actual_role == role, f"Expected role '{role}', but got '{actual_role}'"
    assert actual_status == status, f"Expected status '{status}', but got '{actual_status}'"


@step("a new System User is created for that employee")
def step_impl(context):
    context.execute_steps(u"""
        When I navigate to the Admin page
        And I click add user
        And I fill the user form with role "ESS" and status "Enabled"
        And I click save user
        Then the user should be created successfully
    """)


@step("I click edit for the newly created user")
def step_impl(context):
    context.admin_page.click_edit_user(context.generated_username)


@step('I change user status to "{status}"')
def step_impl(context, status):
    context.admin_page.change_user_status(status)


@step("the user should be updated successfully")
def step_impl(context):
    logger.info("Waiting for success toast (up to 45 seconds)...")
    success = context.admin_page.is_visible(context.admin_page.success_toast, timeout=45000)
    assert success, "Success toast was not displayed after updating user (45s timeout)"
    context.page.wait_for_timeout(3000)


@step('I fill user form with role "{role}", status "{status}", employee "{employee}", username "{username}", password "{password}"')
def step_impl(context, role, status, employee, username, password):
    target_username = username
    if username == "UniqueU":
        target_username = f"user_{uuid.uuid4().hex[:6]}"
        
    context.admin_page.fill_user_form(
        role=role,
        status=status,
        username=target_username,
        password=password,
        employee_name=employee
    )


@step('I should see field validation message "{error_message}" for "{field}"')
def step_impl(context, error_message, field):
    actual_message = context.admin_page.get_field_validation_error(field)
    assert actual_message == error_message, f"Expected error message '{error_message}' for field '{field}', but got '{actual_message}'"
