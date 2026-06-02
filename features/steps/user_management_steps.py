from behave import given, when, then
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
