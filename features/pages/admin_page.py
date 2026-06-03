from playwright.sync_api import Page
from features.pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class AdminPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.admin_header = page.locator("h6:has-text('Admin')")
        self.username_filter = page.locator("div.oxd-input-group:has(label:has-text('Username')) input").first
        self.user_role_filter = page.locator("label:has-text('User Role')").locator("..").locator(".oxd-select-text")
        self.search_button = page.locator("button:has-text('Search')")
        self.reset_button = page.locator("button:has-text('Reset')")
        self.add_button = page.locator("button:has-text('Add')")
        self.add_user_header = page.get_by_role("heading", name="Add User")
        self.save_button = page.get_by_role("button", name="Save")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.results_table = page.locator(".oxd-table")
        self.no_records_message = page.get_by_text("No Records Found").first
        
        # Add User Form Locators (Scoped inside form card container)
        self.user_role_dropdown = page.locator(".orangehrm-card-container div.oxd-input-group:has(label:has-text('User Role'))").locator(".oxd-select-text")
        self.employee_name_autocomplete = page.locator(".orangehrm-card-container input[placeholder='Type for hints...']")
        self.employee_option = page.locator(".oxd-autocomplete-dropdown .oxd-autocomplete-option")
        self.status_dropdown = page.locator(".orangehrm-card-container div.oxd-input-group:has(label:has-text('Status'))").locator(".oxd-select-text")
        self.username_input = page.locator(".orangehrm-card-container div.oxd-input-group:has(label:has-text('Username')) input")
        self.password_input = page.locator(".orangehrm-card-container div.oxd-input-group:has(label:has-text('Password')):not(:has(label:has-text('Confirm'))) input[type='password']")
        self.confirm_password_input = page.locator(".orangehrm-card-container div.oxd-input-group:has(label:has-text('Confirm Password')) input[type='password']")
        self.success_toast = page.locator(".oxd-toast-content")
    
    def is_admin_page_displayed(self) -> bool:
        return self.is_visible(self.admin_header, timeout=15000)
    
    def search_user(self, username: str = None):
        if username:
            self.fill(self.username_filter, username)
        self.click(self.search_button)
        self.page.wait_for_timeout(2000)
        logger.info(f"Searching for user: {username}")
    
    def reset_search(self):
        logger.info("Resetting admin search filters")
        self.click(self.reset_button)
        self.page.wait_for_timeout(2000)

    def is_search_results_displayed(self) -> bool:
        return self.is_visible(self.results_table, timeout=15000) and not self.no_records_message.is_visible()

    def is_no_records_displayed(self) -> bool:
        return self.is_visible(self.no_records_message, timeout=15000)

    def is_username_filter_cleared(self) -> bool:
        self.wait_for_element(self.username_filter)
        return self.username_filter.input_value() == ""

    def click_add_user(self):
        logger.info("Clicking Add User button")
        self.click(self.add_button)

    def is_add_user_form_displayed(self) -> bool:
        return (
            self.is_visible(self.add_user_header, timeout=15000)
            and self.is_visible(self.save_button, timeout=15000)
            and self.is_visible(self.cancel_button, timeout=15000)
        )

    def select_dropdown_option(self, dropdown_locator, option_text: str):
        logger.info(f"Selecting option '{option_text}' in dropdown")
        self.click(dropdown_locator)
        self.page.wait_for_timeout(500)
        option = self.page.locator(".oxd-select-dropdown").get_by_role("option", name=option_text)
        option.click()

    def select_employee_autocomplete(self, employee_name: str):
        logger.info(f"Typing employee name: {employee_name}")
        self.fill(self.employee_name_autocomplete, employee_name)
        # Wait for the dropdown options to appear and load
        self.employee_option.first.wait_for(state="visible", timeout=10000)
        logger.info("Clicking the matching employee suggestion")
        self.employee_option.first.click()

    def fill_user_form(self, role: str, status: str, username: str, password: str, employee_name: str = None):
        if role and role.lower() != "select":
            self.select_dropdown_option(self.user_role_dropdown, role)
        if status and status.lower() != "select":
            self.select_dropdown_option(self.status_dropdown, status)
        if employee_name:
            self.select_employee_autocomplete(employee_name)
        if username:
            self.fill(self.username_input, username)
        if password:
            self.fill(self.password_input, password)
            self.fill(self.confirm_password_input, password)

    def save_user(self):
        logger.info("Saving User")
        self.click(self.save_button)

    def is_success_toast_displayed(self) -> bool:
        return self.is_visible(self.success_toast, timeout=15000)

    def get_user_row_details(self, username: str) -> tuple[str, str]:
        # Locate the row for the username
        row = self.page.locator(".oxd-table-card", has=self.page.locator(f".oxd-table-cell:has-text('{username}')"))
        if not row.is_visible():
            return "", ""
        
        # Col indices:
        # Col 0: Checkbox
        # Col 1: Username
        # Col 2: User Role
        # Col 3: Employee Name
        # Col 4: Status
        role_cell = row.locator(".oxd-table-cell").nth(2)
        status_cell = row.locator(".oxd-table-cell").nth(4)
        
        role = role_cell.text_content().strip()
        status = status_cell.text_content().strip()
        return role, status

    def click_edit_user(self, username: str):
        logger.info(f"Clicking edit for user: {username}")
        row = self.page.locator(".oxd-table-card", has=self.page.locator(f".oxd-table-cell:has-text('{username}')"))
        edit_button = row.locator(".bi-pencil-fill").first
        self.click(edit_button)

    def change_user_status(self, status: str):
        self.select_dropdown_option(self.status_dropdown, status)

    def get_field_validation_error(self, field_label: str) -> str:
        group = self.page.locator(f".orangehrm-card-container div.oxd-input-group:has(label:has-text('{field_label}'))")
        error_span = group.locator("span.oxd-input-field-error-message")
        if self.is_visible(error_span, timeout=5000):
            return error_span.text_content().strip()
        return ""
