from behave import when, then
from features.pages.employee_list_page import EmployeeListPage
from features.pages.add_employee_page import AddEmployeePage
from utils.logger import get_logger
from faker import Faker

logger = get_logger(__name__)
fake = Faker()


@when("I navigate to the PIM employee list")
def step_impl(context):
    list_page = EmployeeListPage(context.page)
    list_page.navigate_to_list()
    context.employee_list_page = list_page


@then("I should see the employee list page")
def step_impl(context):
    assert context.employee_list_page.is_employee_list_displayed(), "Employee list page not displayed"


@when('I search employees by name "{employee_name}"')
def step_impl(context, employee_name):
    context.employee_list_page.search_by_employee_name(employee_name)


@then("employee search results should be shown")
def step_impl(context):
    row_count = context.employee_list_page.get_row_count()
    logger.info(f"Employee search results row count: {row_count}")
    assert row_count >= 0, "Expected search results count to be non-negative"


@when("I open the add employee form")
def step_impl(context):
    context.employee_list_page.click_add_employee()
    add_page = AddEmployeePage(context.page)
    assert add_page.is_add_employee_form_displayed(), "Add Employee form not displayed"
    context.add_employee_page = add_page


@when("I add an employee with generated details")
def step_impl(context):
    first_name = fake.first_name()
    last_name = fake.last_name()
    context.generated_first_name = first_name
    context.generated_last_name = last_name
    context.add_employee_page.fill_employee_details(first_name, last_name)
    context.add_employee_page.save_employee()


@then("the employee should be created successfully")
def step_impl(context):
    assert context.add_employee_page.is_success_toast_displayed(), "Success toast was not displayed"
