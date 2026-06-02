from playwright.sync_api import Page, Locator
from config.config import Config
from utils.logger import get_logger
from features.pages.components.sidebar_component import SidebarComponent

logger = get_logger(__name__)


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = Config.BASE_URL
        self.sidebar = SidebarComponent(page)
    
    def navigate(self, path: str = ""):
        url = f"{self.base_url}{path}"
        logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=Config.TIMEOUT)
    
    def click(self, locator: Locator):
        locator.wait_for(state="visible", timeout=Config.TIMEOUT)
        locator.click()
    
    def fill(self, locator: Locator, text: str):
        locator.wait_for(state="visible", timeout=Config.TIMEOUT)
        locator.fill(text)
    
    def get_text(self, locator: Locator) -> str:
        locator.wait_for(state="visible", timeout=Config.TIMEOUT)
        return locator.text_content()
    
    def wait_for_element(self, locator: Locator, timeout: int = Config.TIMEOUT):
        locator.wait_for(state="visible", timeout=timeout)
    
    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False
