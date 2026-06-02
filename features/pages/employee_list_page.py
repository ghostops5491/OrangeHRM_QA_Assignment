from playwright.sync_api import Page

from features.pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class EmployeeListPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.employee_list_header = page.get_by_role("heading", name="Employee Information")
        self.employee_name_search_input = page.get_by_placeholder("Type for hints...").first
        self.search_button = page.get_by_role("button", name="Search").first
        self.reset_button = page.get_by_role("button", name="Reset").first
        self.add_button = page.get_by_role("button", name="Add")
        self.table_body = page.locator(".oxd-table-body").first
        self.table_rows = page.locator(".oxd-table-card")

    def navigate_to_list(self):
        logger.info("Navigating to PIM employee list")
        self.navigate("/web/index.php/pim/viewEmployeeList")

    def is_employee_list_displayed(self) -> bool:
        return (
            self.is_visible(self.employee_list_header, timeout=15000)
            and self.is_visible(self.table_body, timeout=15000)
        )

    def search_by_employee_name(self, employee_name: str):
        logger.info(f"Searching employee list for: {employee_name}")
        self.fill(self.employee_name_search_input, employee_name)
        self.click(self.search_button)
        self.page.wait_for_timeout(2000)

    def get_row_count(self) -> int:
        return self.table_rows.count()

    def click_add_employee(self):
        logger.info("Opening add employee form from employee list")
        self.click(self.add_button)
