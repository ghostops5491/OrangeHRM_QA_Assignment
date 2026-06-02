from playwright.sync_api import Page
from features.pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.dashboard_header = page.get_by_role("heading", name="Dashboard")
        self.quick_launch_section = page.get_by_text("Quick Launch")
        self.assign_leave_button = page.get_by_role("button", name="Assign Leave")
        self.leave_list_button = page.get_by_role("button", name="Leave List")
        self.user_menu = page.locator(".oxd-userdropdown-tab")
        self.logout_link = page.get_by_role("menuitem", name="Logout")
    
    def is_dashboard_displayed(self) -> bool:
        return self.is_visible(self.dashboard_header, timeout=15000)

    def is_quick_launch_displayed(self) -> bool:
        return (
            self.is_visible(self.quick_launch_section, timeout=15000)
            and self.is_visible(self.assign_leave_button, timeout=15000)
            and self.is_visible(self.leave_list_button, timeout=15000)
        )
    
    def logout(self):
        logger.info("Logging out from application")
        self.click(self.user_menu)
        self.click(self.logout_link)
        logger.info("Logged out successfully")
    
    def go_to_admin_page(self):
        self.sidebar.go_to_admin_page()
    
    def go_to_pim_page(self):
        self.sidebar.go_to_pim_page()

    def go_to_leave_page(self):
        self.sidebar.go_to_leave_page()
