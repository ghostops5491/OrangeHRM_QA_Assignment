from behave import when, then
from features.pages.login_page import LoginPage
from utils.logger import get_logger

logger = get_logger(__name__)


@when("I click on logout")
def step_impl(context):
    context.dashboard_page.logout()


@then("I should be logged out and redirected to login page")
def step_impl(context):
    login_page = LoginPage(context.page)
    assert login_page.is_visible(login_page.login_button), "Not redirected to login page after logout"
