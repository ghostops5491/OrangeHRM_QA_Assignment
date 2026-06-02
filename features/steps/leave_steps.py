from behave import when, then
from features.pages.leave_list_page import LeaveListPage
from utils.logger import get_logger

logger = get_logger(__name__)


@when("I navigate to the Leave list")
def step_impl(context):
    leave_page = LeaveListPage(context.page)
    leave_page.navigate_to_list()
    context.leave_list_page = leave_page


@then("I should see the leave list page")
def step_impl(context):
    assert context.leave_list_page.is_leave_list_displayed(), "Leave list page not displayed"
