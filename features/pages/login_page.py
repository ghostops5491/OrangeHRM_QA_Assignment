from playwright.sync_api import Page
from features.pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input = page.get_by_role("textbox", name="Username")
        self.password_input = page.get_by_role("textbox", name="Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.login_title = page.get_by_role("heading", name="Login")
        self.forgot_password_link = page.get_by_text("Forgot your password?")
        self.reset_password_title = page.get_by_role("heading", name="Reset Password")
        self.error_message = page.locator(".oxd-alert-content-text")
        self.required_fields = page.get_by_text("Required").first
    
    def login(self, username: str, password: str):
        logger.info(f"Attempting to login with username: {username}")
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)
        logger.info("Login button clicked")
    
    def is_error_message_visible(self) -> bool:
        return self.is_visible(self.error_message, timeout=15000)
    
    def is_required_message_visible(self) -> bool:
        return self.is_visible(self.required_fields, timeout=15000)

    def click_forgot_password(self):
        logger.info("Opening forgot password page")
        self.click(self.forgot_password_link)

    def is_reset_password_page_displayed(self) -> bool:
        return self.is_visible(self.reset_password_title, timeout=15000)

    def is_login_page_displayed(self) -> bool:
        return self.is_visible(self.login_title, timeout=15000)
