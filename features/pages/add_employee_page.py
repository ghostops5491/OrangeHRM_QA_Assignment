from playwright.sync_api import Page

from features.pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class AddEmployeePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.add_employee_header = page.get_by_role("heading", name="Add Employee")
        self.first_name_input = page.locator('input[name="firstName"]')
        self.last_name_input = page.locator('input[name="lastName"]')
        self.save_button = page.get_by_role("button", name="Save")
        self.success_toast = page.locator(".oxd-toast-content")

    def is_add_employee_form_displayed(self) -> bool:
        return self.is_visible(self.add_employee_header, timeout=15000)

    def fill_employee_details(self, first_name: str, last_name: str):
        logger.info(f"Filling employee details for: {first_name} {last_name}")
        self.fill(self.first_name_input, first_name)
        self.fill(self.last_name_input, last_name)

    def save_employee(self):
        logger.info("Saving employee details")
        self.click(self.save_button)

    def is_success_toast_displayed(self) -> bool:
        return self.is_visible(self.success_toast, timeout=15000)
