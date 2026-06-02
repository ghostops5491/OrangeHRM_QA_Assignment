from behave import given, when, then
from features.pages.login_page import LoginPage
from features.pages.dashboard_page import DashboardPage
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


@given("I am on the OrangeHRM login page")
def step_impl(context):
    login_page = LoginPage(context.page)
    login_page.navigate()
    context.login_page = login_page


@when("I enter valid username and password")
def step_impl(context):
    context.login_page.login(Config.ADMIN_USERNAME, Config.ADMIN_PASSWORD)


@when("I enter invalid username and password")
def step_impl(context):
    context.login_page.login("invalid", "invalid123")


@when('I enter username "{username}" and password "{password}"')
def step_impl(context, username, password):
    context.login_page.login(username, password)


@when('I enter username state "{username}" and password state "{password}"')
def step_impl(context, username, password):
    resolved_username = "" if username == "blank" else username
    resolved_password = "" if password == "blank" else password
    context.login_page.login(resolved_username, resolved_password)


@when("I click the forgot password link")
def step_impl(context):
    context.login_page.click_forgot_password()


@when("I click on login button")
def step_impl(context):
    pass


@then("I should be logged in successfully")
def step_impl(context):
    dashboard_page = DashboardPage(context.page)
    context.dashboard_page = dashboard_page
    assert dashboard_page.is_dashboard_displayed(), "Dashboard not displayed after login"


@then("I should see an error message")
def step_impl(context):
    assert context.login_page.is_error_message_visible(), "Error message not displayed"


@then("I should see required field messages")
def step_impl(context):
    assert context.login_page.is_required_message_visible(), "Required field message not displayed"


@then("I should see the reset password page")
def step_impl(context):
    assert context.login_page.is_reset_password_page_displayed(), "Reset password page not displayed"
