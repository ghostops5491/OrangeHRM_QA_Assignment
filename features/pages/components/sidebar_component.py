from playwright.sync_api import Page
from utils.logger import get_logger

logger = get_logger(__name__)


class SidebarComponent:
    def __init__(self, page: Page):
        self.page = page
        self.admin_menu = page.get_by_role("link", name="Admin")
        self.pim_menu = page.get_by_role("link", name="PIM")
        self.leave_menu = page.get_by_role("link", name="Leave")

    def go_to_admin_page(self):
        logger.info("Sidebar: Navigating to Admin page")
        self.admin_menu.wait_for(state="visible", timeout=15000)
        self.admin_menu.click()

    def go_to_pim_page(self):
        logger.info("Sidebar: Navigating to PIM page")
        self.pim_menu.wait_for(state="visible", timeout=15000)
        self.pim_menu.click()

    def go_to_leave_page(self):
        logger.info("Sidebar: Navigating to Leave page")
        self.leave_menu.wait_for(state="visible", timeout=15000)
        self.leave_menu.click()
