from playwright.sync_api import Page
from features.pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class AdminPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.admin_header = page.locator("h6:has-text('Admin')")
        self.username_filter = page.locator("div.oxd-input-group:has(label:has-text('Username')) input")
        self.user_role_filter = page.locator("label:has-text('User Role')").locator("..").locator(".oxd-select-text")
        self.search_button = page.locator("button:has-text('Search')")
        self.reset_button = page.locator("button:has-text('Reset')")
        self.add_button = page.locator("button:has-text('Add')")
        self.add_user_header = page.get_by_role("heading", name="Add User")
        self.save_button = page.get_by_role("button", name="Save")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        self.results_table = page.locator(".oxd-table")
        self.no_records_message = page.get_by_text("No Records Found").first
    
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
