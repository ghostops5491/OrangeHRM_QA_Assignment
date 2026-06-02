from playwright.sync_api import Page

from features.pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LeaveListPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.leave_list_header = page.get_by_role("heading", name="Leave List")
        self.search_button = page.get_by_role("button", name="Search").first

    def navigate_to_list(self):
        logger.info("Navigating to Leave list")
        self.navigate("/web/index.php/leave/viewLeaveList")

    def is_leave_list_displayed(self) -> bool:
        return (
            self.is_visible(self.leave_list_header, timeout=15000)
            or self.is_visible(self.search_button, timeout=15000)
        )
